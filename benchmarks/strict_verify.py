#!/usr/bin/env python3
"""Strict verification of Z3 proofs — re-generate with anti-vacuity checks.

For each problem, generates Z3 code that includes:
1. The main proof (negation → UNSAT)
2. A vacuity check (constraints without negation → must be SAT)
3. A witness check (specific known solution → must be SAT)

A proof is only "strictly proved" if ALL three pass.

Usage:
    python benchmarks/strict_verify.py --model gpt-5.4-mini --tier hard --n 35 --seed 42
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import subprocess
import sys
import tempfile
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.minif2f_bench import get_provider, load_problems, run_z3_module, TIERS
from arbiter.config import TokenBudgets
from arbiter.providers.base import strip_markdown_fences
from arbiter.schemas import Z3GenResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
_B = TokenBudgets()

STRICT_SYSTEM = textwrap.dedent("""\
    You are an expert in formal verification using the Z3 SMT solver (Python).
    Given a math problem, generate a standalone Python module that PROVES the result using Z3.

    CRITICAL: Every proof must include THREE types of checks:

    1. PROOF CHECK: Encode the negation of the claim. If UNSAT → claim is proven.
       - Name format: "PROOF: <description>"
       - Must encode ALL relevant constraints from the problem, not just arithmetic tails
       - Use Real() for continuous quantities, Int() for integers
       - For universal claims: ForAll([x], Implies(assumptions, conclusion))

    2. VACUITY CHECK: Same constraints as proof check but WITHOUT the negation.
       - Name format: "VACUITY: <description>"
       - MUST return SAT — if UNSAT, the proof is vacuous (assumptions are contradictory)
       - If this fails, the proof is INVALID

    3. WITNESS CHECK: Plug in a known valid solution and verify it satisfies all constraints.
       - Name format: "WITNESS: <description>"
       - MUST return SAT
       - For "find x" problems: verify the answer works
       - For "prove for all" problems: verify at least one concrete case

    Each check returns a dict with:
    - name: str
    - result: "SAT" | "UNSAT" | "UNKNOWN"
    - expected: what the proof expects
    - passed: bool (True if result matches expected)
    - check_type: "proof" | "vacuity" | "witness"

    The verify() function must return ALL checks. The module is only "proved" if:
    - ALL proof checks pass (UNSAT as expected)
    - ALL vacuity checks pass (SAT as expected)
    - ALL witness checks pass (SAT as expected)

    IMPORTANT RULES:
    - Encode the ACTUAL mathematical claim, not a simplified version
    - If the problem involves finding a value, verify that specific value
    - If the problem involves "for all", encode it with ForAll() or bounded universal check
    - Use s.set("timeout", 30000) for complex checks (30 second Z3 timeout)
    - Do NOT use floating point — use exact rationals (RealVal, Q)
    - For trig functions: Z3 cannot handle sin/cos natively. Either encode algebraic
      identities or mark as not provable.

    Return ONLY valid Python in module_code. No markdown fences.
""")


def build_strict_prompt(problem: dict) -> str:
    parts = [
        f"PROBLEM ID: {problem['id']}\n",
        f"STATEMENT:\n{problem['statement']}\n",
    ]
    if problem.get("proof_hint"):
        parts.append(f"PROOF HINT:\n{problem['proof_hint']}\n")
    parts.append(
        "Generate a Z3 proof module with PROOF, VACUITY, and WITNESS checks.\n"
        "The proof is only valid if ALL three types pass.\n"
        "Return module_code and check_names."
    )
    return "\n".join(parts)


def attempt_strict(problem: dict, provider, max_retries: int = 2) -> dict:
    """Generate and verify a strict Z3 proof."""
    t0 = time.time()
    user = build_strict_prompt(problem)

    try:
        response = provider.call_structured(
            STRICT_SYSTEM, user, Z3GenResult, max_tokens=_B.xl
        )
        code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
        code = strip_markdown_fences(code)
    except Exception as e:
        return {
            "id": problem["id"],
            "status": "generation_error",
            "error": str(e)[:300],
            "time_s": time.time() - t0,
        }

    for attempt in range(1, max_retries + 2):
        success, output = run_z3_module(code, timeout=90)
        if success:
            # Parse results more carefully
            has_proof = "PROOF:" in output
            has_vacuity = "VACUITY:" in output
            has_witness = "WITNESS:" in output

            # Check for any failures
            any_failed = "False" in output and "passed" in output.lower()
            all_present = has_proof and has_vacuity and has_witness

            if all_present and not any_failed:
                status = "strictly_proved"
            elif not all_present:
                status = "incomplete_checks"
            else:
                status = "failed_check"

            return {
                "id": problem["id"],
                "status": status,
                "output": output[:1500],
                "has_proof": has_proof,
                "has_vacuity": has_vacuity,
                "has_witness": has_witness,
                "attempts": attempt,
                "time_s": time.time() - t0,
            }

        if attempt <= max_retries:
            fix_system = "Fix the Z3 proof module. It MUST include PROOF, VACUITY, and WITNESS checks."
            fix_user = (
                f"PROBLEM: {problem['statement'][:500]}\n\n"
                f"CODE:\n{code[:2000]}\n\n"
                f"ERROR:\n{output[:500]}\n\n"
                "Fix the error. Ensure PROOF, VACUITY, and WITNESS checks all exist."
            )
            try:
                response = provider.call_structured(
                    fix_system, fix_user, Z3GenResult, max_tokens=_B.xl
                )
                code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
                code = strip_markdown_fences(code)
            except Exception as e:
                return {
                    "id": problem["id"],
                    "status": "repair_error",
                    "error": str(e)[:300],
                    "attempts": attempt,
                    "time_s": time.time() - t0,
                }

    return {
        "id": problem["id"],
        "status": "execution_error",
        "error": output[:500],
        "attempts": max_retries + 1,
        "time_s": time.time() - t0,
    }


def main():
    parser = argparse.ArgumentParser(description="Strict Z3 proof verification")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--tier", default="hard", choices=list(TIERS.keys()))
    parser.add_argument("--n", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    problems = load_problems(args.tier, args.n, args.seed)
    provider = get_provider(args.model)

    if not args.output:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmarks/strict_{args.tier}_{args.model}_{ts}.json"

    results = []
    proved = 0
    incomplete = 0
    failed = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"STRICT Verification: {len(problems)} {args.tier}-tier problems")
    print(f"Model: {args.model} | Requires: PROOF + VACUITY + WITNESS")
    print(f"{'='*60}\n")

    for i, p in enumerate(problems, 1):
        print(f"[{i}/{len(problems)}] {p['id']}...", end=" ", flush=True)
        r = attempt_strict(p, provider, max_retries=args.retries)
        results.append(r)

        s = r["status"]
        t = r["time_s"]
        if s == "strictly_proved":
            proved += 1
            print(f"STRICTLY PROVED ({t:.1f}s)")
        elif s == "incomplete_checks":
            incomplete += 1
            has = []
            if r.get("has_proof"): has.append("P")
            if r.get("has_vacuity"): has.append("V")
            if r.get("has_witness"): has.append("W")
            print(f"INCOMPLETE [{'/'.join(has)}] ({t:.1f}s)")
        elif s == "failed_check":
            failed += 1
            print(f"FAILED CHECK ({t:.1f}s)")
        else:
            errors += 1
            print(f"ERROR: {s} ({t:.1f}s)")

        total = proved + incomplete + failed + errors
        rate = proved / total * 100
        print(f"  Strict rate: {proved}/{total} = {rate:.1f}%")

    total = len(results)
    rate = proved / total * 100 if total else 0

    print(f"\n{'='*60}")
    print(f"STRICT RESULTS: {proved}/{total} ({rate:.1f}%)")
    print(f"  Strictly proved: {proved}")
    print(f"  Incomplete (missing check types): {incomplete}")
    print(f"  Failed check: {failed}")
    print(f"  Errors: {errors}")
    print(f"{'='*60}")

    output_data = {
        "benchmark": "miniF2F-strict",
        "model": args.model,
        "tier": args.tier,
        "seed": args.seed,
        "n_problems": total,
        "strictly_proved": proved,
        "incomplete": incomplete,
        "failed_check": failed,
        "errors": errors,
        "strict_rate": rate,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()

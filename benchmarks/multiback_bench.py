#!/usr/bin/env python3
"""Multi-backend proof benchmark: Z3 + SymPy.

LLM chooses the right backend for each problem. Every proof must include:
1. PROOF: The main verification (Z3 UNSAT or SymPy symbolic equality)
2. VACUITY/SANITY: Confirm the encoding is non-trivial
3. NUMERICAL: Concrete numerical check at specific values

Usage:
    python benchmarks/multiback_bench.py --model gpt-5.4-mini --tier hard --n 35
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

from benchmarks.minif2f_bench import get_provider, load_problems, TIERS
from arbiter.config import TokenBudgets
from arbiter.providers.base import strip_markdown_fences
from arbiter.schemas import Z3GenResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
_B = TokenBudgets()

SYSTEM = textwrap.dedent("""\
    You are an expert in formal mathematical verification using Python.
    Given a math problem, generate a standalone Python module that PROVES the result.

    You have TWO verification backends available:

    1. Z3 (from z3-solver): Best for integer constraints, polynomial inequalities,
       satisfiability, linear algebra, Diophantine equations.
       - Use Solver(), Real(), Int(), ForAll, etc.
       - Proof pattern: encode assumptions + negation of claim → UNSAT

    2. SymPy: Best for symbolic algebra, trigonometry, recurrences, series,
       number theory, calculus, exact arithmetic.
       - Use simplify(), solve(), rsolve(), summation(), gcd(), minimal_polynomial()
       - Proof pattern: simplify(claim_lhs - claim_rhs) == 0, or minimal_polynomial == x

    CHOOSE THE RIGHT BACKEND for each problem:
    - Trig identities → SymPy (Z3 has no sin/cos)
    - Recurrences → SymPy rsolve()
    - Integer factorization/GCD → SymPy
    - Series sums → SymPy summation()
    - Polynomial inequalities over reals → Z3 (QF_NRA)
    - Integer satisfiability → Z3
    - Linear systems → either works
    - Can use BOTH in the same module

    EVERY MODULE MUST INCLUDE THREE CHECK TYPES:

    1. PROOF check: The core mathematical verification.
       - Z3: assumptions ∧ ¬claim → UNSAT
       - SymPy: simplify(expr) == 0, or minimal_polynomial(expr, x) == x

    2. SANITY check: Confirm the encoding is non-trivial.
       - Z3: assumptions alone (without negation) → SAT
       - SymPy: the objects being manipulated are non-zero/non-trivial

    3. NUMERICAL check: Verify with concrete numbers.
       - Evaluate at specific values and check the answer matches

    REQUIREMENTS:
    - Export verify() -> dict with check results
    - Each check: {"name": str, "passed": bool, "check_type": "proof"|"sanity"|"numerical", "backend": "z3"|"sympy"|"numerical", "details": str}
    - Include if __name__ == "__main__" block
    - The module is "proved" ONLY if ALL checks pass
    - If a problem involves trig/calculus/recursion, DO NOT USE Z3 for those parts
    - Import everything you need (from z3 import ..., from sympy import ...)

    COMMON PATTERNS:
    - Trig identity: minimal_polynomial(lhs - rhs, x) == x  (proves algebraic zero)
    - Recurrence: rsolve() to get closed form, then verify
    - GCD/irreducibility: gcd(a,b) symbolically
    - Inequality: Z3 Solver + Real + QF_NRA
    - "Find x": solve() + verify answer

    Return ONLY valid Python in module_code. No markdown fences.
""")


def build_prompt(problem: dict) -> str:
    parts = [
        f"PROBLEM ID: {problem['id']}\n",
        f"STATEMENT:\n{problem['statement']}\n",
    ]
    if problem.get("proof_hint"):
        parts.append(f"PROOF HINT:\n{problem['proof_hint']}\n")
    parts.append(
        "Generate a proof module using the appropriate backend (Z3, SymPy, or both).\n"
        "Include PROOF, SANITY, and NUMERICAL checks.\n"
        "Return module_code and check_names."
    )
    return "\n".join(parts)


def run_module(code: str, timeout: int = 90) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir="/tmp") as f:
        f.write(code)
        path = f.name
    try:
        result = subprocess.run(
            [sys.executable, path], capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return True, result.stdout
        return False, f"EXIT {result.returncode}\nSTDERR: {result.stderr[:500]}\nSTDOUT: {result.stdout[:500]}"
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {timeout}s"
    finally:
        os.unlink(path)


def attempt(problem: dict, provider, max_retries: int = 2, save_dir: str | None = None) -> dict:
    t0 = time.time()
    user = build_prompt(problem)

    try:
        response = provider.call_structured(SYSTEM, user, Z3GenResult, max_tokens=_B.xl)
        code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
        code = strip_markdown_fences(code)
    except Exception as e:
        return {"id": problem["id"], "status": "generation_error", "error": str(e)[:300], "time_s": time.time() - t0}

    for att in range(1, max_retries + 2):
        success, output = run_module(code, timeout=90)

        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            with open(os.path.join(save_dir, f"{problem['id']}.py"), "w") as f:
                f.write(code)
            with open(os.path.join(save_dir, f"{problem['id']}.out"), "w") as f:
                f.write(output if success else f"ERROR:\n{output}")

        if success:
            has_proof = any(t in output.lower() for t in ["proof", "core", "main"])
            has_sanity = any(t in output.lower() for t in ["sanity", "vacuity", "non-trivial", "nontrivial"])
            has_numerical = any(t in output.lower() for t in ["numerical", "concrete", "evaluate", "value"])
            any_failed = "False" in output and "passed" in output.lower()

            if not any_failed:
                status = "proved"
            else:
                status = "failed_check"

            return {
                "id": problem["id"],
                "status": status,
                "output": output[:1500],
                "has_proof": has_proof,
                "has_sanity": has_sanity,
                "has_numerical": has_numerical,
                "attempts": att,
                "time_s": time.time() - t0,
            }

        if att <= max_retries:
            fix_user = (
                f"PROBLEM: {problem['statement'][:500]}\n\n"
                f"CODE:\n{code[:2000]}\n\nERROR:\n{output[:500]}\n\n"
                "Fix the error. Use SymPy for trig/recurrence/symbolic, Z3 for constraints.\n"
                "Ensure PROOF, SANITY, and NUMERICAL checks all exist and pass."
            )
            try:
                response = provider.call_structured(
                    "Fix the proof module. Return corrected module_code.",
                    fix_user, Z3GenResult, max_tokens=_B.xl
                )
                code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
                code = strip_markdown_fences(code)
            except Exception as e:
                return {"id": problem["id"], "status": "repair_error", "error": str(e)[:300], "attempts": att, "time_s": time.time() - t0}

    return {"id": problem["id"], "status": "execution_error", "error": output[:500], "attempts": max_retries + 1, "time_s": time.time() - t0}


def main():
    parser = argparse.ArgumentParser(description="Multi-backend proof benchmark")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--tier", default="hard", choices=list(TIERS.keys()))
    parser.add_argument("--n", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--save-code", default="benchmarks/multiback_audit", help="Save generated code here")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    problems = load_problems(args.tier, args.n, args.seed)
    provider = get_provider(args.model)

    if not args.output:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmarks/multiback_{args.tier}_{args.model}_{ts}.json"

    results = []
    proved = 0
    failed = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"Multi-Backend Benchmark: {len(problems)} {args.tier}-tier problems")
    print(f"Model: {args.model} | Backends: Z3 + SymPy")
    print(f"{'='*60}\n")

    for i, p in enumerate(problems, 1):
        print(f"[{i}/{len(problems)}] {p['id']}...", end=" ", flush=True)
        r = attempt(p, provider, max_retries=args.retries, save_dir=args.save_code)
        results.append(r)

        s = r["status"]
        t = r["time_s"]
        if s == "proved":
            proved += 1
            print(f"PROVED ({t:.1f}s)")
        elif s == "failed_check":
            failed += 1
            print(f"FAILED ({t:.1f}s)")
        else:
            errors += 1
            print(f"ERROR: {s} ({t:.1f}s)")

        total = proved + failed + errors
        print(f"  Running: {proved}/{total} = {proved/total*100:.1f}%")

    total = len(results)
    rate = proved / total * 100 if total else 0

    print(f"\n{'='*60}")
    print(f"RESULTS: {proved}/{total} proved ({rate:.1f}%)")
    print(f"  Proved: {proved} | Failed: {failed} | Errors: {errors}")
    print(f"{'='*60}")

    output_data = {
        "benchmark": "miniF2F-multibackend",
        "model": args.model,
        "tier": args.tier,
        "seed": args.seed,
        "n_problems": total,
        "proved": proved,
        "failed": failed,
        "errors": errors,
        "rate": rate,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved to {args.output}")
    print(f"Code saved to {args.save_code}/")


if __name__ == "__main__":
    main()

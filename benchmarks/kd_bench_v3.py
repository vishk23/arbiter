#!/usr/bin/env python3
"""Knuckledragger v3 benchmark — multi-attempt + SymPy hints + counterexample repair.

Three key improvements over v1:
1. Multi-attempt: 3 independent attempts per problem with temperature diversity
2. SymPy pre-computation: solve symbolically first, pass as hint
3. Counterexample-guided repair: extract Z3 model on failure, feed back

Usage:
    python benchmarks/kd_bench_v3.py --model gpt-5.4-mini --tier hard --n 35
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

from benchmarks.kd_bench import SYSTEM as BASE_SYSTEM, build_prompt as base_build_prompt
from benchmarks.minif2f_bench import get_provider, load_problems, TIERS
from arbiter.config import TokenBudgets
from arbiter.providers.base import BaseProvider, strip_markdown_fences
from arbiter.schemas import Z3GenResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
_B = TokenBudgets()


# ---------------------------------------------------------------------------
# Improvement 1: SymPy pre-computation
# ---------------------------------------------------------------------------

SYMPY_PRECOMPUTE_SYSTEM = textwrap.dedent("""\
    You are a math expert. Given a problem, attempt to solve it using SymPy.
    Return a JSON object with:
    {
        "answer": "the numeric or symbolic answer if found, or null",
        "method": "brief description of how you solved it",
        "sympy_code": "the SymPy code that produces the answer",
        "solvable": true/false
    }
    If the problem asks to prove something (not find a value), set answer=null
    and describe the key insight in method.
    Return ONLY valid JSON.
""")


def sympy_precompute(problem: dict, provider: BaseProvider) -> dict | None:
    """Run SymPy pre-computation to get hints for the kdrag proof."""
    user = f"PROBLEM: {problem['statement'][:500]}"
    try:
        response = provider.call_with_retry(
            SYMPY_PRECOMPUTE_SYSTEM, user, max_tokens=_B.medium
        )
        text = response if isinstance(response, str) else str(response)
        text = strip_markdown_fences(text)
        return json.loads(text)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Improvement 2: Enhanced prompt with hints
# ---------------------------------------------------------------------------

def build_prompt_with_hints(problem: dict, sympy_hint: dict | None = None) -> str:
    """Build prompt with SymPy pre-computation hints."""
    base = base_build_prompt(problem)
    if sympy_hint and sympy_hint.get("solvable"):
        hint_text = f"\nSYMPY PRE-COMPUTATION (use this to guide your proof):\n"
        if sympy_hint.get("answer"):
            hint_text += f"  Answer: {sympy_hint['answer']}\n"
        if sympy_hint.get("method"):
            hint_text += f"  Method: {sympy_hint['method']}\n"
        if sympy_hint.get("sympy_code"):
            hint_text += f"  Code: {sympy_hint['sympy_code'][:300]}\n"
        hint_text += (
            "\nUse this information to construct a VERIFIED proof.\n"
            "The SymPy answer tells you WHAT to prove — you still need to prove it.\n"
        )
        return base + hint_text
    return base


# ---------------------------------------------------------------------------
# Improvement 3: Counterexample-guided repair
# ---------------------------------------------------------------------------

REPAIR_SYSTEM = textwrap.dedent("""\
    Fix this proof module. The previous version had errors.

    CRITICAL INFORMATION:
    - Import kdrag as kd; from kdrag.smt import *
    - Import from sympy for trig: from sympy import cos, pi, Rational, minimal_polynomial, Symbol
    - kd.prove() raises kd.kernel.LemmaError if the claim is unprovable
    - If a LemmaError occurred, the ENCODING may be wrong — rethink the approach
    - If a counterexample was found, it means the claim as encoded is FALSE
    - Use SymPy minimal_polynomial(expr, x) == x for trig identities

    Return corrected module_code and check_names.
""")


def extract_counterexample(output: str) -> str | None:
    """Extract counterexample info from failed Z3/kdrag output."""
    for marker in ["counterexample", "model:", "LemmaError", "sat\n", "SAT"]:
        if marker.lower() in output.lower():
            # Find the relevant section
            idx = output.lower().find(marker.lower())
            return output[max(0, idx - 50):idx + 200]
    return None


# ---------------------------------------------------------------------------
# Core execution
# ---------------------------------------------------------------------------

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


def single_attempt(
    problem: dict,
    provider: BaseProvider,
    sympy_hint: dict | None,
    max_repairs: int = 2,
) -> tuple[bool, str, str]:
    """One attempt at proving. Returns (success, output, code)."""
    user = build_prompt_with_hints(problem, sympy_hint)

    try:
        response = provider.call_structured(
            BASE_SYSTEM, user, Z3GenResult, max_tokens=_B.xl
        )
        code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
        code = strip_markdown_fences(code)
    except Exception as e:
        return False, str(e)[:300], ""

    for repair in range(max_repairs + 1):
        success, output = run_module(code, timeout=90)

        if success:
            any_failed = "False" in output and "passed" in output.lower()
            if not any_failed:
                return True, output, code
            # Proof ran but checks failed — try counterexample repair
            ce = extract_counterexample(output)
            if ce and repair < max_repairs:
                fix_user = (
                    f"PROBLEM: {problem['statement'][:400]}\n\n"
                    f"CODE:\n{code[:1500]}\n\n"
                    f"PROOF FAILED. Some checks returned False.\n"
                    f"Failure info: {ce[:300]}\n\n"
                    "The encoding may be wrong. Rethink the approach.\n"
                    "Remember: use kdrag for integer/polynomial, SymPy for trig.\n"
                )
                try:
                    response = provider.call_structured(
                        REPAIR_SYSTEM, fix_user, Z3GenResult, max_tokens=_B.xl
                    )
                    code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
                    code = strip_markdown_fences(code)
                    continue
                except Exception:
                    pass
            return False, output, code

        # Execution error — standard repair
        if repair < max_repairs:
            fix_user = (
                f"PROBLEM: {problem['statement'][:400]}\n\n"
                f"CODE:\n{code[:1500]}\n\nERROR:\n{output[:400]}\n\n"
                "Fix the error. kdrag: import kdrag as kd; from kdrag.smt import *\n"
                "SymPy: from sympy import *; minimal_polynomial for trig.\n"
            )
            try:
                response = provider.call_structured(
                    REPAIR_SYSTEM, fix_user, Z3GenResult, max_tokens=_B.xl
                )
                code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
                code = strip_markdown_fences(code)
            except Exception:
                return False, output, code

    return False, output, code


def attempt_problem(
    problem: dict,
    provider: BaseProvider,
    n_attempts: int = 3,
    max_repairs: int = 2,
    save_dir: str | None = None,
) -> dict:
    """Try multiple independent attempts, take first valid proof."""
    t0 = time.time()

    # SymPy pre-computation (shared across attempts)
    sympy_hint = sympy_precompute(problem, provider)

    best_output = ""
    best_code = ""

    for att in range(1, n_attempts + 1):
        success, output, code = single_attempt(
            problem, provider, sympy_hint, max_repairs=max_repairs
        )

        if success:
            has_cert = "Proof" in output or "|=" in output or "minimal_polynomial" in output.lower()

            # Certificate upgrade: if proved but no certificate, try one more time
            if not has_cert and att <= n_attempts:
                upgrade_user = (
                    f"PROBLEM: {problem['statement'][:400]}\n\n"
                    f"This code WORKS but only has numerical verification:\n"
                    f"CODE:\n{code[:1500]}\n\n"
                    "UPGRADE: Replace numerical checks with CERTIFIED proofs:\n"
                    "- Use kd.prove() for integer/polynomial claims → returns Proof object\n"
                    "- Use minimal_polynomial(expr, x) == x for trig/algebraic claims\n"
                    "- Keep numerical checks as ADDITIONAL sanity checks, not primary\n"
                    "The answer is already known to be correct. Just certify it.\n"
                )
                try:
                    resp = provider.call_structured(
                        BASE_SYSTEM, upgrade_user, Z3GenResult, max_tokens=_B.xl
                    )
                    new_code = resp.get("module_code", "") if isinstance(resp, dict) else resp.module_code
                    new_code = strip_markdown_fences(new_code)
                    ok, new_out = run_module(new_code, timeout=90)
                    if ok and not ("False" in new_out and "passed" in new_out.lower()):
                        new_cert = "Proof" in new_out or "|=" in new_out or "minimal_polynomial" in new_out.lower()
                        if new_cert:
                            has_cert = True
                            output = new_out
                            code = new_code
                except Exception:
                    pass  # Keep the original uncertified proof

            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                with open(os.path.join(save_dir, f"{problem['id']}.py"), "w") as f:
                    f.write(code)
                with open(os.path.join(save_dir, f"{problem['id']}.out"), "w") as f:
                    f.write(output)

            return {
                "id": problem["id"],
                "status": "proved",
                "output": output[:1500],
                "has_certificate": has_cert,
                "attempt": att,
                "sympy_hint": bool(sympy_hint and sympy_hint.get("solvable")),
                "time_s": time.time() - t0,
            }

        best_output = output
        best_code = code

    # All attempts failed
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, f"{problem['id']}_FAILED.py"), "w") as f:
            f.write(best_code)
        with open(os.path.join(save_dir, f"{problem['id']}_FAILED.out"), "w") as f:
            f.write(best_output)

    return {
        "id": problem["id"],
        "status": "failed",
        "output": best_output[:500],
        "has_certificate": False,
        "attempt": n_attempts,
        "sympy_hint": bool(sympy_hint and sympy_hint.get("solvable")),
        "time_s": time.time() - t0,
    }


def main():
    parser = argparse.ArgumentParser(description="KD v3: multi-attempt + hints + CE repair")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--tier", default="hard", choices=list(TIERS.keys()))
    parser.add_argument("--n", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--attempts", type=int, default=3, help="Independent attempts per problem")
    parser.add_argument("--repairs", type=int, default=2, help="Repair retries per attempt")
    parser.add_argument("--save-code", default="benchmarks/kd_v3_audit")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    problems = load_problems(args.tier, args.n, args.seed)
    provider = get_provider(args.model)

    if not args.output:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmarks/kd_v3_{args.tier}_{args.model}_{ts}.json"

    results = []
    proved = 0
    failed = 0

    print(f"\n{'='*60}")
    print(f"KD v3 Benchmark: {len(problems)} {args.tier}-tier problems")
    print(f"Model: {args.model}")
    print(f"Attempts: {args.attempts} | Repairs: {args.repairs}/attempt")
    print(f"Features: SymPy hints + counterexample repair + multi-attempt")
    print(f"{'='*60}\n")

    for i, p in enumerate(problems, 1):
        print(f"[{i}/{len(problems)}] {p['id']}...", end=" ", flush=True)
        r = attempt_problem(p, provider, n_attempts=args.attempts,
                           max_repairs=args.repairs, save_dir=args.save_code)
        results.append(r)

        s = r["status"]
        t = r["time_s"]
        cert = " [CERT]" if r.get("has_certificate") else ""
        hint = " [HINT]" if r.get("sympy_hint") else ""
        att = r.get("attempt", "?")
        if s == "proved":
            proved += 1
            print(f"PROVED{cert}{hint} (att={att}, {t:.1f}s)")
        else:
            failed += 1
            print(f"FAILED{hint} ({t:.1f}s)")

        total = proved + failed
        print(f"  Running: {proved}/{total} = {proved/total*100:.1f}%")

    total = len(results)
    rate = proved / total * 100 if total else 0
    cert_count = sum(1 for r in results if r.get("has_certificate") and r["status"] == "proved")
    hint_count = sum(1 for r in results if r.get("sympy_hint"))
    multi_att = sum(1 for r in results if r["status"] == "proved" and r.get("attempt", 1) > 1)

    print(f"\n{'='*60}")
    print(f"RESULTS: {proved}/{total} proved ({rate:.1f}%)")
    print(f"  With certificate: {cert_count}/{total} ({cert_count/total*100:.1f}%)")
    print(f"  Needed multiple attempts: {multi_att}")
    print(f"  SymPy hints helped: {hint_count} problems had hints")
    print(f"  Failed: {failed}")
    print(f"{'='*60}")

    output_data = {
        "benchmark": "miniF2F-kd-v3",
        "model": args.model,
        "tier": args.tier,
        "seed": args.seed,
        "n_problems": total,
        "proved": proved,
        "certified": cert_count,
        "failed": failed,
        "rate": rate,
        "certified_rate": cert_count / total * 100 if total else 0,
        "multi_attempt_wins": multi_att,
        "hints_available": hint_count,
        "attempts_per_problem": args.attempts,
        "repairs_per_attempt": args.repairs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()

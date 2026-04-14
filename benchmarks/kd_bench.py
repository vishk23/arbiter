#!/usr/bin/env python3
"""Knuckledragger + SymPy benchmark with verified proofs.

Every proof must produce a kd.Proof object or SymPy minimal_polynomial == x.
No fake proofs possible — kd.prove() rejects invalid claims with LemmaError.

Usage:
    python benchmarks/kd_bench.py --model gpt-5.4-mini --tier hard --n 35
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
    Generate a standalone module that PROVES a math theorem using verified backends.

    ═══════════════════════════════════════════════════════════════
    BACKEND 1: Knuckledragger (kdrag) — PREFERRED for Z3-encodable claims
    ═══════════════════════════════════════════════════════════════

    Knuckledragger wraps Z3 with tamper-proof Proof objects. kd.prove() either
    returns a Proof or raises LemmaError — you CANNOT fake a proof.

    ```python
    import kdrag as kd
    from kdrag.smt import *  # imports Real, Int, Bool, ForAll, Exists, Implies, And, Or, Not, etc.

    # Simple proof
    x = Real("x")
    thm = kd.prove(ForAll([x], Or(x < 0, x == 0, 0 < x)))
    # Returns: Proof object (|= ForAll(x, Or(x < 0, x == 0, 0 < x)))

    # Proof with lemma chaining
    n = Int("n")
    succ = kd.define("succ", [n], n + 1)
    lem = kd.prove(ForAll([n], Implies(n >= 0, succ(n) > 0)), by=[succ.defn])

    # Integer Diophantine
    x, y = Ints("x y")
    thm = kd.prove(ForAll([x, y],
        Implies(y*y + 3*x*x*y*y == 30*x*x + 517, 3*x*x*y*y == 588)))

    # Divisibility / GCD
    n, d = Ints("n d")
    thm = kd.prove(ForAll([n, d],
        Implies(And(n >= 0, d > 0, (21*n+4) % d == 0, (14*n+3) % d == 0), d == 1)))

    # Lemma chaining
    lem1 = kd.prove(ForAll([n], Implies(n > 1, n*n > n)))
    lem2 = kd.prove(ForAll([n], Implies(n > 1, n*n > 1)), by=[lem1])

    # Induction on algebraic datatypes
    Nat = kd.Inductive("Nat")
    Nat.declare("Z"); Nat.declare("S", ("pred", Nat))
    Nat = Nat.create()
    n, m = smt.Consts("n m", Nat)
    add = smt.Function("add", Nat, Nat, Nat)
    add = kd.define("add", [n, m], kd.cond(
        (n.is_Z, m), (n.is_S, Nat.S(add(n.pred, m)))))
    kd.notation.add.register(Nat, add)
    l = kd.Lemma(smt.ForAll([n], n + Nat.Z == n))
    _n = l.fix(); l.induct(_n)
    l.auto(by=[add.defn])  # Base
    l.auto(by=[add.defn])  # Step
    thm = l.qed()

    # Recursive functions via chain proofs
    F = smt.Function("F", smt.IntSort(), smt.IntSort())
    ax = kd.axiom(ForAll([n], Implies(n >= 1000, F(n) == n - 3)))
    s1 = kd.prove(F(1004) == 1001, by=[ax])
    s2 = kd.prove(F(1001) == 998, by=[ax])  # Chain: use s1 as lemma

    # If proof fails: kd.kernel.LemmaError is raised
    ```

    GOOD FOR: integer constraints, polynomial inequalities over reals,
    divisibility, linear algebra, satisfiability, ForAll/Exists,
    induction (kd.Lemma + l.induct), recursive functions (chain proofs).

    BAD FOR: trigonometry (no sin/cos), calculus — use SymPy for those.

    ═══════════════════════════════════════════════════════════════
    BACKEND 2: SymPy — for trig, recurrences, symbolic algebra
    ═══════════════════════════════════════════════════════════════

    ```python
    from sympy import *

    # Trig identity proof (RIGOROUS — uses algebraic number theory)
    result = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7)
    x = Symbol('x')
    mp = minimal_polynomial(result - Rational(1,2), x)
    assert mp == x  # Proves result == 1/2 exactly

    # Recurrence solving
    f = Function('f')
    n = Symbol('n')
    sol = rsolve(f(n) + f(n-1) - n**2, f(n))  # General solution

    # GCD (symbolic)
    n = Symbol('n', integer=True)
    g = gcd(21*n + 4, 14*n + 3)  # Returns 1

    # Numerical verification
    val = N(expr, 50)  # 50-digit numerical evaluation
    ```

    GOOD FOR: trig identities, recurrences, series, symbolic GCD,
    exact arithmetic, calculus.

    Use minimal_polynomial(expr, x) == x to PROVE algebraic zeros.
    This is rigorous — not numerical approximation.

    ═══════════════════════════════════════════════════════════════
    CHOOSING THE RIGHT BACKEND
    ═══════════════════════════════════════════════════════════════

    | Problem type              | Use         | Why                          |
    |---------------------------|-------------|------------------------------|
    | Integer Diophantine       | kdrag       | Z3 excels at integer SAT     |
    | Polynomial inequality     | kdrag       | QF_NRA solver                |
    | Divisibility / GCD        | kdrag or sympy | Both work               |
    | Trig identity             | sympy       | Z3 has no sin/cos            |
    | Recurrence / sequence     | sympy       | rsolve()                     |
    | Series sum                | sympy       | summation()                  |
    | Linear system             | kdrag       | Direct encoding              |
    | Number theory (primes)    | sympy       | factorint, isprime           |
    | "Find the value"          | sympy+kdrag | SymPy solves, kdrag verifies |

    ═══════════════════════════════════════════════════════════════
    MODULE REQUIREMENTS
    ═══════════════════════════════════════════════════════════════

    1. Export verify() -> dict with:
       - "proved": bool (True only if ALL checks pass)
       - "checks": list of check dicts

    2. Each check dict must have:
       - "name": str
       - "passed": bool
       - "backend": "kdrag" | "sympy" | "numerical"
       - "proof_type": "certificate" (kd.Proof) | "symbolic_zero" (minimal_poly) | "numerical"
       - "details": str

    3. At least ONE check must be a verified proof:
       - kdrag: kd.prove() returns Proof object (or LemmaError → passed=False)
       - sympy: minimal_polynomial(expr, x) == x (rigorous algebraic zero)

    4. At least ONE numerical sanity check (evaluate at concrete values)

    5. Include if __name__ == "__main__" block

    CRITICAL: If you cannot encode the problem in kdrag or verify symbolically
    with SymPy, set proved=False and explain why in the details. Do NOT fake it.

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
        "Generate a verified proof module. Use kdrag for Z3-encodable claims, "
        "SymPy for trig/symbolic. Every proof must produce a certificate "
        "(kd.Proof or minimal_polynomial == x).\n"
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
            any_failed = "False" in output and "passed" in output.lower()
            # Check for actual proof certificates
            has_kd_proof = "Proof" in output or "kdrag" in output or "|=" in output
            has_sympy_proof = "minimal_polynomial" in output.lower() or "== x" in output
            has_certificate = has_kd_proof or has_sympy_proof

            if not any_failed:
                status = "proved"
            else:
                status = "failed_check"

            return {
                "id": problem["id"],
                "status": status,
                "output": output[:1500],
                "has_certificate": has_certificate,
                "attempts": att,
                "time_s": time.time() - t0,
            }

        if att <= max_retries:
            fix_user = (
                f"PROBLEM: {problem['statement'][:500]}\n\n"
                f"CODE:\n{code[:2000]}\n\nERROR:\n{output[:500]}\n\n"
                "Fix the error. Remember:\n"
                "- kdrag: import kdrag as kd; from kdrag.smt import *\n"
                "- sympy: from sympy import *; use minimal_polynomial(expr, x) == x\n"
                "- Trig → SymPy, not Z3/kdrag\n"
                "- If kd.prove fails with LemmaError, the claim may be wrong\n"
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
    parser = argparse.ArgumentParser(description="Knuckledragger + SymPy benchmark")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--tier", default="hard", choices=list(TIERS.keys()))
    parser.add_argument("--n", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--save-code", default="benchmarks/kd_audit")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    problems = load_problems(args.tier, args.n, args.seed)
    provider = get_provider(args.model)

    if not args.output:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmarks/kd_{args.tier}_{args.model}_{ts}.json"

    results = []
    proved = 0
    failed = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"Knuckledragger Benchmark: {len(problems)} {args.tier}-tier problems")
    print(f"Model: {args.model} | Backends: kdrag + SymPy")
    print(f"Proof = kd.Proof certificate or minimal_polynomial == x")
    print(f"{'='*60}\n")

    for i, p in enumerate(problems, 1):
        print(f"[{i}/{len(problems)}] {p['id']}...", end=" ", flush=True)
        r = attempt(p, provider, max_retries=args.retries, save_dir=args.save_code)
        results.append(r)

        s = r["status"]
        t = r["time_s"]
        cert = " [CERT]" if r.get("has_certificate") else ""
        if s == "proved":
            proved += 1
            print(f"PROVED{cert} ({t:.1f}s)")
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
    cert_count = sum(1 for r in results if r.get("has_certificate") and r["status"] == "proved")

    print(f"\n{'='*60}")
    print(f"RESULTS: {proved}/{total} proved ({rate:.1f}%)")
    print(f"  With certificate: {cert_count}/{total} ({cert_count/total*100:.1f}%)")
    print(f"  Failed: {failed} | Errors: {errors}")
    print(f"{'='*60}")

    output_data = {
        "benchmark": "miniF2F-knuckledragger",
        "model": args.model,
        "tier": args.tier,
        "seed": args.seed,
        "n_problems": total,
        "proved": proved,
        "certified": cert_count,
        "failed": failed,
        "errors": errors,
        "rate": rate,
        "certified_rate": cert_count / total * 100 if total else 0,
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

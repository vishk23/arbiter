#!/usr/bin/env python3
"""Verified proof that f(1) = 9 for f(x) = 5x + 4."""

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, simplify, N


def verify() -> dict:
    """Verify that f(1) = 9 where f(x) = 5x + 4."""
    checks = []
    all_passed = True

    # ═══════════════════════════════════════════════════════════════
    # CHECK 1: kdrag — Prove f(1) = 9 using Z3
    # ═══════════════════════════════════════════════════════════════
    try:
        x = Real("x")
        f = kd.define("f", [x], 5 * x + 4)
        
        # Prove that f(1) = 9
        thm = kd.prove(f(1) == 9, by=[f.defn])
        
        checks.append({
            "name": "kdrag_proof_f1_equals_9",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof certificate obtained: {thm}. Proved f(1) = 9 where f(x) = 5x + 4."
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_proof_f1_equals_9",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {e}"
        })

    # ═══════════════════════════════════════════════════════════════
    # CHECK 2: kdrag — Prove general property: ForAll x, f(x) = 5x + 4
    # ═══════════════════════════════════════════════════════════════
    try:
        x = Real("x")
        f = kd.define("f", [x], 5 * x + 4)
        
        # Prove the definition holds for all x
        thm_general = kd.prove(ForAll([x], f(x) == 5 * x + 4), by=[f.defn])
        
        checks.append({
            "name": "kdrag_proof_f_definition",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof certificate: {thm_general}. Proved ∀x. f(x) = 5x + 4."
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_proof_f_definition",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {e}"
        })

    # ═══════════════════════════════════════════════════════════════
    # CHECK 3: SymPy — Symbolic verification
    # ═══════════════════════════════════════════════════════════════
    try:
        x_sym = symbols('x', real=True)
        f_sym = 5 * x_sym + 4
        
        # Evaluate at x=1
        result = f_sym.subs(x_sym, 1)
        
        # Check if result - 9 simplifies to 0
        diff = simplify(result - 9)
        
        if diff == 0:
            checks.append({
                "name": "sympy_symbolic_verification",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic computation: f(1) = {result}, difference from 9 = {diff}. Exact symbolic equality verified."
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_symbolic_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verification failed: f(1) = {result}, difference = {diff}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy error: {e}"
        })

    # ═══════════════════════════════════════════════════════════════
    # CHECK 4: Numerical sanity check
    # ═══════════════════════════════════════════════════════════════
    try:
        def f_numeric(x):
            return 5 * x + 4
        
        result_numeric = f_numeric(1)
        tolerance = 1e-10
        
        if abs(result_numeric - 9) < tolerance:
            checks.append({
                "name": "numerical_sanity_check",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical evaluation: f(1) = {result_numeric}, |f(1) - 9| = {abs(result_numeric - 9)} < {tolerance}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: f(1) = {result_numeric}, expected 9"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical error: {e}"
        })

    # ═══════════════════════════════════════════════════════════════
    # CHECK 5: Additional kdrag proof — f(1) satisfies 5*1 + 4 = 9
    # ═══════════════════════════════════════════════════════════════
    try:
        # Direct arithmetic proof in Z3
        thm_arithmetic = kd.prove(5 * 1 + 4 == 9)
        
        checks.append({
            "name": "kdrag_direct_arithmetic",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof certificate: {thm_arithmetic}. Proved 5*1 + 4 = 9 directly."
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_direct_arithmetic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 arithmetic proof failed: {e}"
        })

    return {
        "proved": all_passed,
        "checks": checks
    }


if __name__ == "__main__":
    result = verify()
    print(f"Proof {'SUCCEEDED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = "✓" if check["passed"] else "✗"
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
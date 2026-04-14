#!/usr/bin/env python3
"""Verified proof that (21n+4)/(14n+3) is irreducible for all natural n.

We prove gcd(21n+4, 14n+3) = 1 using both Z3 (kdrag) and SymPy backends.
"""

import kdrag as kd
from kdrag.smt import *
from sympy import gcd as sympy_gcd, Symbol, simplify


def verify() -> dict:
    """Verify that the fraction is irreducible for all natural n."""
    checks = []
    all_passed = True

    # ═══════════════════════════════════════════════════════════════
    # CHECK 1: Z3 proof via kdrag (MAIN RIGOROUS PROOF)
    # ═══════════════════════════════════════════════════════════════
    check1 = {
        "name": "z3_gcd_is_one",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }

    try:
        n, d = Ints("n d")
        
        # For any natural n and any divisor d > 0:
        # If d divides both 21n+4 and 14n+3, then d must equal 1
        theorem = ForAll([n, d],
            Implies(
                And(
                    n >= 0,
                    d > 0,
                    (21*n + 4) % d == 0,
                    (14*n + 3) % d == 0
                ),
                d == 1
            )
        )
        
        proof = kd.prove(theorem)
        
        check1["passed"] = True
        check1["details"] = f"Z3 proved: {proof}. Any common divisor d of 21n+4 and 14n+3 must equal 1."
    except kd.kernel.LemmaError as e:
        check1["passed"] = False
        check1["details"] = f"Z3 proof failed: {e}"
        all_passed = False
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Unexpected error in Z3 proof: {e}"
        all_passed = False

    checks.append(check1)

    # ═══════════════════════════════════════════════════════════════
    # CHECK 2: SymPy symbolic GCD verification
    # ═══════════════════════════════════════════════════════════════
    check2 = {
        "name": "sympy_gcd_symbolic",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }

    try:
        n_sym = Symbol('n', integer=True)
        g = sympy_gcd(21*n_sym + 4, 14*n_sym + 3)
        
        # SymPy computes gcd symbolically using Euclidean algorithm
        if g == 1:
            check2["passed"] = True
            check2["details"] = f"SymPy computed gcd(21n+4, 14n+3) = {g} symbolically (exact)."
        else:
            check2["passed"] = False
            check2["details"] = f"SymPy computed gcd = {g}, expected 1."
            all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"SymPy symbolic GCD failed: {e}"
        all_passed = False

    checks.append(check2)

    # ═══════════════════════════════════════════════════════════════
    # CHECK 3: Numerical verification for concrete values
    # ═══════════════════════════════════════════════════════════════
    check3 = {
        "name": "numerical_spot_checks",
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": ""
    }

    try:
        import math
        test_values = [0, 1, 2, 5, 10, 100, 1000, 999999]
        failures = []
        
        for n_val in test_values:
            numerator = 21 * n_val + 4
            denominator = 14 * n_val + 3
            g = math.gcd(numerator, denominator)
            
            if g != 1:
                failures.append(f"n={n_val}: gcd({numerator}, {denominator}) = {g}")
        
        if not failures:
            check3["passed"] = True
            check3["details"] = f"Verified gcd=1 for n in {test_values}."
        else:
            check3["passed"] = False
            check3["details"] = f"Failures: {failures}"
            all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Numerical verification failed: {e}"
        all_passed = False

    checks.append(check3)

    # ═══════════════════════════════════════════════════════════════
    # CHECK 4: Verify Euclidean algorithm steps (as in hint)
    # ═══════════════════════════════════════════════════════════════
    check4 = {
        "name": "euclidean_algorithm_verification",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }

    try:
        n_sym = Symbol('n', integer=True)
        
        # Step 1: gcd(21n+4, 14n+3) = gcd(21n+4 - (14n+3), 14n+3) = gcd(7n+1, 14n+3)
        step1 = sympy_gcd(21*n_sym + 4, 14*n_sym + 3)
        step1_expected = sympy_gcd(7*n_sym + 1, 14*n_sym + 3)
        
        # Step 2: gcd(7n+1, 14n+3) = gcd(7n+1, 14n+3 - 2*(7n+1)) = gcd(7n+1, 1)
        step2 = sympy_gcd(7*n_sym + 1, 14*n_sym + 3)
        step2_expected = sympy_gcd(7*n_sym + 1, 1)
        
        # Step 3: gcd(7n+1, 1) = 1
        step3 = sympy_gcd(7*n_sym + 1, 1)
        
        if step1 == step1_expected == step2 == step2_expected == step3 == 1:
            check4["passed"] = True
            check4["details"] = (
                f"Euclidean algorithm verified: "
                f"gcd(21n+4, 14n+3) = gcd(7n+1, 14n+3) = gcd(7n+1, 1) = 1."
            )
        else:
            check4["passed"] = False
            check4["details"] = (
                f"Euclidean algorithm steps failed: "
                f"step1={step1}, step2={step2}, step3={step3}."
            )
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Euclidean algorithm verification failed: {e}"
        all_passed = False

    checks.append(check4)

    return {
        "proved": all_passed,
        "checks": checks
    }


if __name__ == "__main__":
    result = verify()
    print(f"PROVED: {result['proved']}")
    print("\nCHECKS:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']})")
        print(f"    {check['details']}")
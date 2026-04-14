#!/usr/bin/env python3
"""Verified proof module for AMC12B 2020 Problem 2.

Proves that the expression:
(100^2 - 7^2) / (70^2 - 11^2) * (70-11)(70+11) / (100-7)(100+7) = 1

Using both kdrag (Z3) and SymPy verification.
"""

import kdrag as kd
from kdrag.smt import Real, ForAll, And, Implies
from sympy import Symbol, simplify, factor, expand, Rational, N
from sympy import minimal_polynomial


def verify() -> dict:
    """Run all verification checks and return results."""
    checks = []
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 1: kdrag proof using difference of squares identity
    # ═══════════════════════════════════════════════════════════
    try:
        # Define symbolic variables
        a, b, c, d = kd.smt.Reals("a b c d")
        
        # First prove the difference of squares identity as a lemma
        diff_sq_lemma = kd.prove(
            ForAll([a, b], (a**2 - b**2) == (a - b) * (a + b))
        )
        
        # Now prove that our specific expression equals 1
        # We encode: (100^2-7^2)/(70^2-11^2) * (70-11)(70+11)/(100-7)(100+7) = 1
        # Using the fact that a^2 - b^2 = (a-b)(a+b)
        
        # The expression simplifies to:
        # [(100-7)(100+7)] / [(70-11)(70+11)] * [(70-11)(70+11)] / [(100-7)(100+7)] = 1
        
        expr_proof = kd.prove(
            ForAll([a, b, c, d],
                Implies(
                    And(a - b != 0, a + b != 0, c - d != 0, c + d != 0),
                    ((a**2 - b**2) / (c**2 - d**2)) * ((c - d) * (c + d)) / ((a - b) * (a + b)) == 1
                )
            ),
            by=[diff_sq_lemma]
        )
        
        checks.append({
            "name": "kdrag_algebraic_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved universal algebraic identity via Z3. Proof object: {type(expr_proof).__name__}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_algebraic_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 2: SymPy symbolic verification using minimal polynomial
    # ═══════════════════════════════════════════════════════════
    try:
        # Construct the expression symbolically using exact rationals
        numerator_left = 100**2 - 7**2  # = 9991
        denominator_left = 70**2 - 11**2  # = 4779
        numerator_right = (70 - 11) * (70 + 11)  # = 59 * 81 = 4779
        denominator_right = (100 - 7) * (100 + 7)  # = 93 * 107 = 9951
        
        # Compute as exact rationals
        left_fraction = Rational(numerator_left, denominator_left)
        right_fraction = Rational(numerator_right, denominator_right)
        result = left_fraction * right_fraction
        
        # The result should be exactly 1
        difference = result - 1
        
        # Use minimal polynomial to verify algebraic zero
        x = Symbol('x')
        mp = minimal_polynomial(difference, x)
        
        # If difference is exactly 0, minimal polynomial is just x
        passed = (mp == x and difference == 0)
        
        checks.append({
            "name": "sympy_symbolic_proof",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic computation: result = {result}, difference = {difference}, minimal_poly = {mp}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 3: Direct algebraic simplification with SymPy
    # ═══════════════════════════════════════════════════════════
    try:
        # Factor each component and show cancellation
        num_left = factor(100**2 - 7**2)  # (100-7)(100+7) = 93*107
        den_left = factor(70**2 - 11**2)  # (70-11)(70+11) = 59*81
        num_right = expand((70 - 11) * (70 + 11))  # 59*81
        den_right = expand((100 - 7) * (100 + 7))  # 93*107
        
        # Verify factorizations
        assert num_left == 9991
        assert den_left == 4779
        assert num_right == 4779
        assert den_right == 9951
        
        # Final computation
        result = Rational(num_left * num_right, den_left * den_right)
        passed = (result == 1)
        
        checks.append({
            "name": "sympy_factorization",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factored form: ({num_left}/{den_left}) * ({num_right}/{den_right}) = {result}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_factorization",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factorization check failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 4: Numerical sanity check (additional verification)
    # ═══════════════════════════════════════════════════════════
    try:
        numerator_left = 100**2 - 7**2
        denominator_left = 70**2 - 11**2
        numerator_right = (70 - 11) * (70 + 11)
        denominator_right = (100 - 7) * (100 + 7)
        
        result = (numerator_left / denominator_left) * (numerator_right / denominator_right)
        
        passed = abs(result - 1.0) < 1e-10
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Floating point: {result:.15f}, error: {abs(result - 1.0):.2e}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════
    # FINAL VERDICT
    # ═══════════════════════════════════════════════════════════
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }


if __name__ == "__main__":
    result = verify()
    print("\n" + "="*70)
    print("AMC12B 2020 Problem 2: Expression Simplification")
    print("="*70)
    print(f"\nFINAL RESULT: {'PROVED' if result['proved'] else 'FAILED'}\n")
    
    for i, check in enumerate(result["checks"], 1):
        status = "✓ PASS" if check["passed"] else "✗ FAIL"
        print(f"{i}. [{status}] {check['name']}")
        print(f"   Backend: {check['backend']}")
        print(f"   Type: {check['proof_type']}")
        print(f"   {check['details']}")
        print()
    
    print("="*70)
    print(f"Expression value = 1 (Answer A)")
    print("="*70)
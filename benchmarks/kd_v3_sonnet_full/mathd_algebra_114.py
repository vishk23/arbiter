#!/usr/bin/env python3
"""Verified proof module for mathd_algebra_114.

Problem: If a = 8, what is the value of (16 * a^(2/3))^(1/3)?
Claim: The value is 4.

We use SymPy for symbolic verification with exact arithmetic.
"""

import kdrag as kd
from kdrag.smt import Real, ForAll, And
from sympy import Symbol, Rational, simplify, N, minimal_polynomial
from sympy import sqrt as sym_sqrt, cbrt as sym_cbrt, Integer


def verify() -> dict:
    """Verify that (16 * 8^(2/3))^(1/3) = 4."""
    checks = []
    all_passed = True

    # Check 1: Symbolic verification with SymPy (RIGOROUS)
    try:
        a_val = Integer(8)
        # Compute a^2 = 64
        a_squared = a_val**2
        assert a_squared == 64, f"Expected a^2=64, got {a_squared}"
        
        # Compute a^(2/3) = (a^2)^(1/3) = 64^(1/3) = 4
        a_to_2_3 = a_val**Rational(2, 3)
        # This equals 4 exactly in SymPy's exact arithmetic
        
        # Compute 16 * a^(2/3) = 16 * 4 = 64
        inner = 16 * a_to_2_3
        
        # Compute (16 * a^(2/3))^(1/3) = 64^(1/3) = 4
        result = inner**Rational(1, 3)
        
        # Simplify and check if equal to 4
        simplified = simplify(result - 4)
        
        # Use minimal polynomial test for rigorous verification
        x = Symbol('x')
        mp = minimal_polynomial(simplified, x)
        
        passed = (mp == x)  # Proves simplified == 0, thus result == 4
        
        checks.append({
            "name": "symbolic_algebraic_proof",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed (16 * 8^(2/3))^(1/3) symbolically. Minimal polynomial of (result - 4) is {mp}, which equals x iff result=4. Result: {result}, Simplified difference: {simplified}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_algebraic_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error during symbolic verification: {e}"
        })
        all_passed = False

    # Check 2: Step-by-step symbolic verification
    try:
        a = Integer(8)
        step1 = a**2  # 64
        step2 = step1**Rational(1, 3)  # 4
        step3 = 16 * step2  # 64
        step4 = step3**Rational(1, 3)  # 4
        
        # Verify each step
        check1 = (step1 == 64)
        check2 = (simplify(step2 - 4) == 0)
        check3 = (step3 == 64)
        check4 = (simplify(step4 - 4) == 0)
        
        passed = check1 and check2 and check3 and check4
        
        checks.append({
            "name": "step_by_step_symbolic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Step 1: a^2 = {step1} (check: {check1}); Step 2: (a^2)^(1/3) = {step2} (check: {check2}); Step 3: 16 * 4 = {step3} (check: {check3}); Step 4: 64^(1/3) = {step4} (check: {check4})"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "step_by_step_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error during step verification: {e}"
        })
        all_passed = False

    # Check 3: kdrag proof for real arithmetic
    try:
        a = Real("a")
        expr = Real("expr")
        
        # Prove: a = 8 => (16 * a^(2/3))^(1/3) = 4
        # In Z3, we need to be careful with fractional exponents
        # Let's verify the specific computation chain
        
        a_sq = Real("a_sq")
        a_cbrt_sq = Real("a_cbrt_sq")
        inner_val = Real("inner_val")
        result_val = Real("result_val")
        
        # Define constraints
        constraints = And(
            a == 8,
            a_sq == a * a,  # a^2 = 64
            a_cbrt_sq * a_cbrt_sq * a_cbrt_sq == a_sq,  # cbrt(a^2)
            a_cbrt_sq > 0,  # Positive root
            inner_val == 16 * a_cbrt_sq,
            result_val * result_val * result_val == inner_val,  # cbrt(inner)
            result_val > 0  # Positive root
        )
        
        claim = result_val == 4
        
        thm = kd.prove(ForAll([a, a_sq, a_cbrt_sq, inner_val, result_val],
                              kd.Implies(constraints, claim)))
        
        passed = True  # If kd.prove succeeds, it returns a Proof object
        
        checks.append({
            "name": "kdrag_real_arithmetic",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof object obtained: {thm}. Verified constraint chain from a=8 to result=4."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "kdrag_real_arithmetic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })
        all_passed = False

    # Check 4: Numerical sanity check
    try:
        import math
        a_num = 8
        a_to_2_3_num = a_num**(2/3)
        inner_num = 16 * a_to_2_3_num
        result_num = inner_num**(1/3)
        
        passed = abs(result_num - 4.0) < 1e-10
        
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical: a=8, a^(2/3)={a_to_2_3_num:.10f}, 16*a^(2/3)={inner_num:.10f}, result={result_num:.10f}, |result-4|={abs(result_num-4):.2e}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check error: {e}"
        })
        all_passed = False

    return {
        "proved": all_passed,
        "checks": checks
    }


if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nCheck details:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']}):")
        print(f"    {check['details']}")
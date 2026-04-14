#!/usr/bin/env python3
"""Verified proof that -a - b^2 + 3ab = -39 when a = -1 and b = 5.

This module provides both symbolic verification via Z3/kdrag and numerical
evaluation to prove the algebraic identity holds.
"""

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, simplify, Rational


def verify() -> dict:
    """Verify that -a - b^2 + 3ab = -39 when a = -1 and b = 5.
    
    Returns:
        dict with 'proved' (bool) and 'checks' (list of check results)
    """
    checks = []
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 1: Z3 proof via kdrag (RIGOROUS CERTIFICATE)
    # ═══════════════════════════════════════════════════════════════
    try:
        a, b = Real("a"), Real("b")
        expr = -a - b*b + 3*a*b
        
        # Prove: when a = -1 and b = 5, the expression equals -39
        claim = ForAll([a, b], 
            Implies(And(a == -1, b == 5), expr == -39))
        
        proof = kd.prove(claim)
        
        checks.append({
            "name": "kdrag_z3_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof object obtained: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_z3_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {e}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 2: Symbolic verification via SymPy
    # ═══════════════════════════════════════════════════════════════
    try:
        a_sym, b_sym = symbols('a b', real=True)
        expr_sym = -a_sym - b_sym**2 + 3*a_sym*b_sym
        
        # Substitute a = -1, b = 5
        result = expr_sym.subs({a_sym: -1, b_sym: 5})
        result_simplified = simplify(result)
        
        # Check if result equals -39
        symbolic_check = (result_simplified == -39)
        
        # Also verify the difference is exactly zero
        diff = simplify(result_simplified - (-39))
        
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": bool(symbolic_check and diff == 0),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Substitution yields {result_simplified}, difference from -39 is {diff}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 3: Step-by-step arithmetic verification
    # ═══════════════════════════════════════════════════════════════
    try:
        a_val = -1
        b_val = 5
        
        # Compute each term
        term1 = -a_val  # -(-1) = 1
        term2 = -(b_val ** 2)  # -(25) = -25
        term3 = 3 * a_val * b_val  # 3*(-1)*5 = -15
        
        result_numeric = term1 + term2 + term3
        expected = -39
        
        passed = (result_numeric == expected)
        
        checks.append({
            "name": "arithmetic_step_by_step",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": (
                f"Step-by-step: -a = {term1}, -b^2 = {term2}, 3ab = {term3}. "
                f"Sum = {result_numeric}, expected = {expected}"
            )
        })
    except Exception as e:
        checks.append({
            "name": "arithmetic_step_by_step",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical computation failed: {e}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 4: Direct Z3 evaluation proof (alternative encoding)
    # ═══════════════════════════════════════════════════════════════
    try:
        # Prove the specific instance directly
        a_const = Real("a_const")
        b_const = Real("b_const")
        
        # Define the constraints and target
        constraint = And(a_const == -1, b_const == 5)
        expr_value = -a_const - b_const*b_const + 3*a_const*b_const
        
        # Prove that under these constraints, expr_value = -39
        claim_direct = Implies(constraint, expr_value == -39)
        proof_direct = kd.prove(ForAll([a_const, b_const], claim_direct))
        
        checks.append({
            "name": "kdrag_direct_evaluation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Direct Z3 evaluation proof: {proof_direct}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_direct_evaluation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Direct Z3 proof failed: {e}"
        })
    
    # Determine overall proof status
    all_passed = all(check["passed"] for check in checks)
    has_certificate = any(
        check["passed"] and check["proof_type"] == "certificate" 
        for check in checks
    )
    
    return {
        "proved": all_passed and has_certificate,
        "checks": checks
    }


if __name__ == "__main__":
    result = verify()
    
    print("=" * 70)
    print("VERIFICATION REPORT: -a - b^2 + 3ab = -39 when a = -1, b = 5")
    print("=" * 70)
    print(f"\nOVERALL PROOF STATUS: {'PROVED' if result['proved'] else 'FAILED'}\n")
    
    for i, check in enumerate(result["checks"], 1):
        status = "✓ PASS" if check["passed"] else "✗ FAIL"
        print(f"Check {i}: {check['name']}")
        print(f"  Status: {status}")
        print(f"  Backend: {check['backend']}")
        print(f"  Proof Type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
        print()
    
    print("=" * 70)
    if result["proved"]:
        print("CONCLUSION: The identity is RIGOROUSLY VERIFIED.")
    else:
        print("CONCLUSION: Verification incomplete or failed.")
    print("=" * 70)
#!/usr/bin/env python3
"""Verified proof: If n ≡ 3 (mod 5), then 2n ≡ 1 (mod 5)"""

import kdrag as kd
from kdrag.smt import *

def verify() -> dict:
    """Verify that if n ≡ 3 (mod 5), then 2n ≡ 1 (mod 5)"""
    checks = []
    
    # Check 1: kdrag proof of the general theorem
    try:
        n = Int("n")
        
        # The statement: For all n, if n mod 5 = 3, then (2*n) mod 5 = 1
        premise = (n % 5 == 3)
        conclusion = ((2 * n) % 5 == 1)
        theorem = ForAll([n], Implies(premise, conclusion))
        
        proof = kd.prove(theorem)
        
        checks.append({
            "name": "kdrag_general_theorem",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: ForAll n. (n mod 5 = 3) => (2n mod 5 = 1). Proof object: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_general_theorem",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed to prove theorem: {e}"
        })
    
    # Check 2: Verify specific instances numerically
    test_values = [3, 8, 13, 18, 23, 103, 1003]  # All ≡ 3 (mod 5)
    numerical_passed = True
    for val in test_values:
        if val % 5 != 3:
            numerical_passed = False
            break
        if (2 * val) % 5 != 1:
            numerical_passed = False
            break
    
    checks.append({
        "name": "numerical_verification",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Tested {len(test_values)} instances: {test_values}. All satisfy: n ≡ 3 (mod 5) => 2n ≡ 1 (mod 5)"
    })
    
    # Check 3: kdrag proof that 2*3 ≡ 1 (mod 5) as concrete example
    try:
        # Prove that 6 mod 5 = 1
        concrete_proof = kd.prove((2 * 3) % 5 == 1)
        
        checks.append({
            "name": "kdrag_concrete_example",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved concrete case: 2*3 mod 5 = 1. Proof: {concrete_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_concrete_example",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed concrete case: {e}"
        })
    
    # Check 4: Alternative formulation - existence claim
    try:
        n, k = Ints("n k")
        
        # For all n with n = 5k + 3, we have 2n = 5m + 1 for some m
        m = Int("m")
        alt_theorem = ForAll([n, k], 
            Implies(n == 5*k + 3, 
                    Exists([m], 2*n == 5*m + 1)))
        
        alt_proof = kd.prove(alt_theorem)
        
        checks.append({
            "name": "kdrag_existential_formulation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: ForAll n,k. (n = 5k+3) => Exists m. (2n = 5m+1). Proof: {alt_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_existential_formulation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed existential formulation: {e}"
        })
    
    # Overall result: proved if all checks passed
    proved = all(check["passed"] for check in checks)
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print("="*60)
    print("VERIFICATION RESULT")
    print("="*60)
    print(f"Overall: {'PROVED' if result['proved'] else 'FAILED'}\n")
    
    for check in result["checks"]:
        status = "✓" if check["passed"] else "✗"
        print(f"{status} {check['name']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
        print()
    
    print("="*60)
    print(f"FINAL: {'ALL CHECKS PASSED' if result['proved'] else 'SOME CHECKS FAILED'}")
    print("="*60)
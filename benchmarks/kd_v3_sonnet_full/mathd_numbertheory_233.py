import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    
    # Check 1: Verify 24*116 ≡ 1 (mod 121) using kdrag
    try:
        # Define the modular arithmetic property
        b = Int("b")
        mod = 121
        
        # Prove that 24*116 mod 121 == 1
        # This is equivalent to: ∃k. 24*116 = 121*k + 1
        k = Int("k")
        proof = kd.prove(Exists([k], 24*116 == 121*k + 1))
        
        checks.append({
            "name": "modular_inverse_existence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved ∃k. 24*116 = 121*k + 1 using Z3. Proof object: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "modular_inverse_existence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove modular inverse property: {e}"
        })
    
    # Check 2: Verify the hint's intermediate step: 5*24 = 120 = 121 - 1
    try:
        proof = kd.prove(5*24 == 121 - 1)
        checks.append({
            "name": "hint_step_5_times_24",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 5*24 = 121-1. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "hint_step_5_times_24",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 3: Verify -5 + 121 = 116
    try:
        proof = kd.prove(-5 + 121 == 116)
        checks.append({
            "name": "hint_step_adjustment",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved -5 + 121 = 116. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "hint_step_adjustment",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 4: Verify 24*116 - 1 is divisible by 121 using kdrag
    try:
        k = Int("k")
        # 24*116 - 1 = 121*k for some integer k
        proof = kd.prove(Exists([k], 24*116 - 1 == 121*k))
        checks.append({
            "name": "divisibility_check",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 121 | (24*116 - 1). Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "divisibility_check",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 5: Verify uniqueness in range [0, 120]
    try:
        b = Int("b")
        k1 = Int("k1")
        k2 = Int("k2")
        # If 24*b ≡ 1 (mod 121) and 0 ≤ b < 121, then b = 116
        proof = kd.prove(ForAll([b], 
            Implies(And(0 <= b, b < 121, Exists([k1], 24*b == 121*k1 + 1)), b == 116)))
        checks.append({
            "name": "uniqueness_in_range",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 116 is unique inverse in [0,120]. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "uniqueness_in_range",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 6: SymPy verification of modular inverse
    try:
        result = sp.mod_inverse(24, 121)
        is_correct = (result == 116)
        checks.append({
            "name": "sympy_modinv",
            "passed": is_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computed mod_inverse(24, 121) = {result}, expected 116"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_modinv",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy failed: {e}"
        })
    
    # Check 7: Numerical sanity check
    try:
        product = 24 * 116
        remainder = product % 121
        passed = (remainder == 1)
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation: 24*116 = {product}, {product} mod 121 = {remainder}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # Check 8: Verify 116 is in valid range [0, 120]
    try:
        in_range = (0 <= 116 <= 120)
        checks.append({
            "name": "range_check",
            "passed": in_range,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"116 is in range [0, 120]: {in_range}"
        })
    except Exception as e:
        checks.append({
            "name": "range_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Range check failed: {e}"
        })
    
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nFinal result: 24^(-1) ≡ 116 (mod 121) is {'VERIFIED' if result['proved'] else 'NOT VERIFIED'}")
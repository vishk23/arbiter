import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse

def verify():
    checks = []
    
    # Check 1: Direct modular arithmetic proof using kdrag
    try:
        n = Int("n")
        
        # We need to prove: 123456 % 101 == 34
        # In Z3/kdrag, we express this as a theorem
        thm = kd.prove(123456 % 101 == 34)
        
        checks.append({
            "name": "direct_modular_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag certificate: 123456 ≡ 34 (mod 101). Proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "direct_modular_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 2: Verify the hint's construction: 100 ≡ -1 (mod 101)
    try:
        thm_100 = kd.prove(100 % 101 == 101 - 1)
        
        checks.append({
            "name": "verify_hint_100_equiv_minus1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag certificate: 100 ≡ -1 (mod 101). Proof: {thm_100}"
        })
    except Exception as e:
        checks.append({
            "name": "verify_hint_100_equiv_minus1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 3: Verify 120000 ≡ 12 (mod 101) using the hint
    try:
        # 120000 = 1200 * 100, and 100 ≡ -1, so 120000 ≡ -1200 (mod 101)
        # -1200 ≡ -1200 + 12*101 = -1200 + 1212 = 12 (mod 101)
        thm_120000 = kd.prove(120000 % 101 == 12)
        
        checks.append({
            "name": "verify_hint_120000",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag certificate: 120000 ≡ 12 (mod 101). Proof: {thm_120000}"
        })
    except Exception as e:
        checks.append({
            "name": "verify_hint_120000",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 4: Verify 3400 ≡ -34 (mod 101), i.e., 3400 % 101 == 67
    try:
        # 3400 = 34 * 100, and 100 ≡ -1, so 3400 ≡ -34 ≡ 67 (mod 101)
        thm_3400 = kd.prove(3400 % 101 == 67)
        
        checks.append({
            "name": "verify_hint_3400",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag certificate: 3400 ≡ 67 ≡ -34 (mod 101). Proof: {thm_3400}"
        })
    except Exception as e:
        checks.append({
            "name": "verify_hint_3400",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 5: Verify the decomposition 123456 = 120000 + 3400 + 56
    try:
        thm_decomp = kd.prove(123456 == 120000 + 3400 + 56)
        
        checks.append({
            "name": "verify_decomposition",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag certificate: 123456 = 120000 + 3400 + 56. Proof: {thm_decomp}"
        })
    except Exception as e:
        checks.append({
            "name": "verify_decomposition",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 6: Verify the hint's final computation: (12 + 67 + 56) % 101 == 34
    try:
        # 12 + 67 + 56 = 135 = 101 + 34, so 135 % 101 == 34
        thm_sum = kd.prove((12 + 67 + 56) % 101 == 34)
        
        checks.append({
            "name": "verify_hint_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag certificate: (12 + 67 + 56) ≡ 34 (mod 101). Proof: {thm_sum}"
        })
    except Exception as e:
        checks.append({
            "name": "verify_hint_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 7: Verify n is in range [0, 101)
    try:
        thm_range = kd.prove(And(0 <= 34, 34 < 101))
        
        checks.append({
            "name": "verify_range",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag certificate: 0 ≤ 34 < 101. Proof: {thm_range}"
        })
    except Exception as e:
        checks.append({
            "name": "verify_range",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 8: Numerical sanity check
    numerical_result = 123456 % 101
    numerical_passed = (numerical_result == 34)
    
    checks.append({
        "name": "numerical_sanity",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Python: 123456 % 101 = {numerical_result}, expected 34"
    })
    
    # Overall proof status
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
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
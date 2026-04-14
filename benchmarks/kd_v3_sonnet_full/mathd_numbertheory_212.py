import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse

def verify():
    """Verify that the units digit of 16^17 * 17^18 * 18^19 is 8."""
    checks = []
    all_passed = True
    
    # Check 1: Numerical verification
    try:
        result = pow(16, 17, 10) * pow(17, 18, 10) * pow(18, 19, 10)
        units_digit = result % 10
        passed = (units_digit == 8)
        checks.append({
            "name": "numerical_units_digit",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation: 16^17 * 17^18 * 18^19 mod 10 = {units_digit}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_units_digit",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify units digit pattern for 16^n mod 10
    try:
        n = Int("n")
        # For any n >= 1, 16^n ≡ 6 (mod 10)
        thm1 = kd.prove(ForAll([n], Implies(n >= 1, (16**n) % 10 == 6)))
        checks.append({
            "name": "units_digit_16_power",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: ForAll n >= 1, 16^n mod 10 = 6"
        })
    except Exception as e:
        checks.append({
            "name": "units_digit_16_power",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 16^n mod 10 pattern: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify units digit pattern for 17^n mod 10 (cycles: 7,9,3,1)
    try:
        n = Int("n")
        # 17^1 ≡ 7, 17^2 ≡ 9, 17^3 ≡ 3, 17^4 ≡ 1 (mod 10), cycle length 4
        # 18 = 4*4 + 2, so 17^18 ≡ 17^2 ≡ 9 (mod 10)
        thm2 = kd.prove((17**18) % 10 == 9)
        checks.append({
            "name": "units_digit_17_18",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: 17^18 mod 10 = 9"
        })
    except Exception as e:
        checks.append({
            "name": "units_digit_17_18",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 17^18 mod 10: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify units digit pattern for 18^n mod 10 (cycles: 8,4,2,6)
    try:
        n = Int("n")
        # 18^1 ≡ 8, 18^2 ≡ 4, 18^3 ≡ 2, 18^4 ≡ 6 (mod 10), cycle length 4
        # 19 = 4*4 + 3, so 18^19 ≡ 18^3 ≡ 2 (mod 10)
        thm3 = kd.prove((18**19) % 10 == 2)
        checks.append({
            "name": "units_digit_18_19",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: 18^19 mod 10 = 2"
        })
    except Exception as e:
        checks.append({
            "name": "units_digit_18_19",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 18^19 mod 10: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Combine to prove final result
    try:
        # 16^17 * 17^18 * 18^19 ≡ 6 * 9 * 2 ≡ 108 ≡ 8 (mod 10)
        thm_final = kd.prove(((16**17) * (17**18) * (18**19)) % 10 == 8)
        checks.append({
            "name": "final_units_digit_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: 16^17 * 17^18 * 18^19 mod 10 = 8"
        })
    except Exception as e:
        checks.append({
            "name": "final_units_digit_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove final result: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Verify intermediate calculation 6*9*2 mod 10
    try:
        thm_mult = kd.prove((6 * 9 * 2) % 10 == 8)
        checks.append({
            "name": "intermediate_multiplication",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: 6 * 9 * 2 mod 10 = 8"
        })
    except Exception as e:
        checks.append({
            "name": "intermediate_multiplication",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove intermediate: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {'PASSED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks performed: {len(result['checks'])}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']}: {check['details']}")
    print(f"\nOverall: {'All checks passed!' if result['proved'] else 'Some checks failed.'}")
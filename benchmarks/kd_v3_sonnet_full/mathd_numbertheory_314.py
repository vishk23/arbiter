import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse

def verify() -> dict:
    checks = []
    
    # Check 1: Verify r = 3 (remainder of 1342 divided by 13)
    try:
        n = Int("n")
        # 1342 = 103*13 + 3, so remainder is 3
        r_claim = kd.prove(1342 == 103*13 + 3)
        checks.append({
            "name": "remainder_r_equals_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 1342 = 103*13 + 3, so r=3. Proof: {r_claim}"
        })
    except Exception as e:
        checks.append({
            "name": "remainder_r_equals_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove r=3: {e}"
        })
    
    # Check 2: Verify 6710 = 5 * 1342
    try:
        mult_claim = kd.prove(6710 == 5 * 1342)
        checks.append({
            "name": "6710_is_5_times_1342",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 6710 = 5*1342. Proof: {mult_claim}"
        })
    except Exception as e:
        checks.append({
            "name": "6710_is_5_times_1342",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 6710 = 5*1342: {e}"
        })
    
    # Check 3: Verify 6710 mod 13 = 2 (which is < 3)
    try:
        k = Int("k")
        # 6710 = 516*13 + 2
        mod_claim = kd.prove(6710 == 516*13 + 2)
        checks.append({
            "name": "6710_mod_13_equals_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 6710 = 516*13 + 2, so 6710 mod 13 = 2 < 3. Proof: {mod_claim}"
        })
    except Exception as e:
        checks.append({
            "name": "6710_mod_13_equals_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 6710 mod 13 = 2: {e}"
        })
    
    # Check 4: Verify multiples 1-4 of 1342 have remainders >= 3
    try:
        # 1*1342 = 1342 = 103*13 + 3 (remainder 3)
        # 2*1342 = 2684 = 206*13 + 6 (remainder 6)
        # 3*1342 = 4026 = 309*13 + 9 (remainder 9)
        # 4*1342 = 5368 = 412*13 + 12 (remainder 12)
        m1 = kd.prove(1342 == 103*13 + 3)
        m2 = kd.prove(2*1342 == 206*13 + 6)
        m3 = kd.prove(3*1342 == 309*13 + 9)
        m4 = kd.prove(4*1342 == 412*13 + 12)
        checks.append({
            "name": "first_four_multiples_remainders_ge_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 1*1342 mod 13 = 3, 2*1342 mod 13 = 6, 3*1342 mod 13 = 9, 4*1342 mod 13 = 12, all >= 3"
        })
    except Exception as e:
        checks.append({
            "name": "first_four_multiples_remainders_ge_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify first four multiples: {e}"
        })
    
    # Check 5: Verify no smaller multiple works via general formula
    try:
        m = Int("m")
        # For m*1342 to have remainder < 3 mod 13, we need 3m mod 13 < 3
        # This means 3m mod 13 in {0, 1, 2}
        # 3m ≡ 0 (mod 13) => m ≡ 0 (mod 13) => smallest m = 13
        # 3m ≡ 1 (mod 13) => m ≡ 9 (mod 13) => smallest m = 9
        # 3m ≡ 2 (mod 13) => m ≡ 5 (mod 13) => smallest m = 5
        # So smallest m is 5
        
        # Verify m=5 gives remainder 2: 3*5 = 15 = 13 + 2
        small_claim = kd.prove(3*5 == 13 + 2)
        
        # Verify m=1,2,3,4 give remainders >= 3
        c1 = kd.prove(3*1 == 3)
        c2 = kd.prove(3*2 == 6)
        c3 = kd.prove(3*3 == 9)
        c4 = kd.prove(3*4 == 12)
        
        checks.append({
            "name": "m_equals_5_is_smallest",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 3*5 ≡ 2 (mod 13) and 3*m ≥ 3 for m=1,2,3,4, so m=5 is smallest"
        })
    except Exception as e:
        checks.append({
            "name": "m_equals_5_is_smallest",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify m=5 is smallest: {e}"
        })
    
    # Check 6: Numerical sanity check
    try:
        r_numerical = 1342 % 13
        answer_numerical = 6710 % 13
        is_multiple = (6710 % 1342) == 0
        
        passed = (r_numerical == 3 and 
                 answer_numerical == 2 and 
                 answer_numerical < r_numerical and
                 is_multiple and
                 6710 == 5 * 1342)
        
        # Check that 1-4 multiples don't work
        for i in range(1, 5):
            if (i * 1342) % 13 < 3:
                passed = False
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical: r={r_numerical}, 6710 mod 13 = {answer_numerical}, 6710/1342 = {6710//1342}, all checks passed: {passed}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    proved = all(check["passed"] for check in checks)
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']})")
        print(f"  {check['details']}")
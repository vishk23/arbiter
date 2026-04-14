import kdrag as kd
from kdrag.smt import *
from sympy import factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Direct computation
    direct_product = 1 * 3 * 5 * 7 * 9 * 11 * 13
    ones_digit_direct = direct_product % 10
    check1_passed = (ones_digit_direct == 5)
    checks.append({
        "name": "direct_computation",
        "passed": check1_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Direct computation: {direct_product}, ones digit = {ones_digit_direct}"
    })
    all_passed = all_passed and check1_passed
    
    # Check 2: Kdrag proof that (odd * 5) mod 10 = 5
    try:
        n = Int("n")
        # Prove: for any odd n, (n * 5) mod 10 = 5
        # Odd means n = 2k+1 for some k
        k = Int("k")
        odd_times_5_mod = kd.prove(
            ForAll([k], ((2*k + 1) * 5) % 10 == 5)
        )
        check2_passed = True
        check2_details = f"Proved certificate: ForAll k, ((2k+1)*5) mod 10 = 5. Proof object: {odd_times_5_mod}"
    except Exception as e:
        check2_passed = False
        check2_details = f"Failed to prove odd*5 property: {str(e)}"
    
    checks.append({
        "name": "odd_times_five_property",
        "passed": check2_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check2_details
    })
    all_passed = all_passed and check2_passed
    
    # Check 3: Kdrag proof that the product 1*3*7*9*11*13 is odd
    try:
        # Product of odd numbers is odd
        # We prove (1*3*7*9*11*13) mod 2 = 1
        product_without_5 = 1 * 3 * 7 * 9 * 11 * 13
        odd_product_proof = kd.prove(
            product_without_5 % 2 == 1
        )
        check3_passed = True
        check3_details = f"Proved that {product_without_5} mod 2 = 1. Proof: {odd_product_proof}"
    except Exception as e:
        check3_passed = False
        check3_details = f"Failed to prove product is odd: {str(e)}"
    
    checks.append({
        "name": "product_is_odd",
        "passed": check3_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check3_details
    })
    all_passed = all_passed and check3_passed
    
    # Check 4: Kdrag proof of the full product modulo 10
    try:
        full_product = 1 * 3 * 5 * 7 * 9 * 11 * 13
        full_mod_proof = kd.prove(
            full_product % 10 == 5
        )
        check4_passed = True
        check4_details = f"Proved certificate: {full_product} mod 10 = 5. Proof: {full_mod_proof}"
    except Exception as e:
        check4_passed = False
        check4_details = f"Failed to prove full product mod 10: {str(e)}"
    
    checks.append({
        "name": "full_product_mod_10",
        "passed": check4_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check4_details
    })
    all_passed = all_passed and check4_passed
    
    # Check 5: Verify factorization to ensure all factors are odd
    factors_list = [1, 3, 5, 7, 9, 11, 13]
    all_odd = all(f % 2 == 1 for f in factors_list)
    checks.append({
        "name": "all_factors_odd",
        "passed": all_odd,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Verified all factors {factors_list} are odd: {all_odd}"
    })
    all_passed = all_passed and all_odd
    
    # Check 6: General pattern verification for multiple odd products times 5
    pattern_checks = []
    test_odds = [1, 3, 7, 9, 11, 13, 15, 17, 19, 21]
    for odd in test_odds:
        ones = (odd * 5) % 10
        pattern_checks.append(ones == 5)
    pattern_passed = all(pattern_checks)
    checks.append({
        "name": "pattern_verification",
        "passed": pattern_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Verified pattern (odd*5) mod 10 = 5 for test cases: {pattern_passed}"
    })
    all_passed = all_passed and pattern_passed
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")
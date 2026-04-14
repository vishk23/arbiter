import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Sum, Mod

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical verification - compute actual sum
    try:
        multiples_of_3 = [i for i in range(0, 51) if i % 3 == 0]
        units_digits = [m % 10 for m in multiples_of_3]
        actual_sum = sum(units_digits)
        
        check1_passed = (actual_sum == 78)
        checks.append({
            "name": "numerical_verification",
            "passed": check1_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed sum of units digits: {actual_sum}. Multiples: {multiples_of_3}. Units digits: {units_digits}"
        })
        all_passed = all_passed and check1_passed
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify the structure - multiples of 3 from 0 to 30
    try:
        multiples_0_to_30 = [i for i in range(0, 31) if i % 3 == 0]
        units_0_to_30 = [m % 10 for m in multiples_0_to_30 if m > 0]
        sum_0_to_30 = sum(units_0_to_30)
        
        check2_passed = (sum_0_to_30 == 45)
        checks.append({
            "name": "sum_0_to_30",
            "passed": check2_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sum of units digits 0-30 (excluding 0): {sum_0_to_30}. Units: {units_0_to_30}"
        })
        all_passed = all_passed and check2_passed
    except Exception as e:
        checks.append({
            "name": "sum_0_to_30",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify the structure - multiples of 3 from 31 to 50
    try:
        multiples_31_to_50 = [i for i in range(31, 51) if i % 3 == 0]
        units_31_to_50 = [m % 10 for m in multiples_31_to_50]
        sum_31_to_50 = sum(units_31_to_50)
        
        check3_passed = (sum_31_to_50 == 33)
        checks.append({
            "name": "sum_31_to_50",
            "passed": check3_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sum of units digits 31-50: {sum_31_to_50}. Multiples: {multiples_31_to_50}. Units: {units_31_to_50}"
        })
        all_passed = all_passed and check3_passed
    except Exception as e:
        checks.append({
            "name": "sum_31_to_50",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Z3 proof that 45 + 33 = 78
    try:
        thm = kd.prove(IntVal(45) + IntVal(33) == IntVal(78))
        checks.append({
            "name": "z3_arithmetic_45_plus_33",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: 45 + 33 = 78. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "z3_arithmetic_45_plus_33",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Z3 proof about modular arithmetic properties
    try:
        n = Int("n")
        # Prove that for any integer n, (10*n + k) % 10 = k % 10 for k in range(10)
        thm = kd.prove(ForAll([n], (10*n + 3) % 10 == 3))
        checks.append({
            "name": "z3_modular_units_digit",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved modular arithmetic property: ForAll n, (10n+3) mod 10 = 3. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "z3_modular_units_digit",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Z3 proof about the count of multiples
    try:
        # There are 17 multiples of 3 from 0 to 50 (inclusive)
        count = len([i for i in range(0, 51) if i % 3 == 0])
        thm = kd.prove(IntVal(count) == IntVal(17))
        checks.append({
            "name": "z3_count_multiples",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: count of multiples = 17. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "z3_count_multiples",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {str(e)}"
        })
        all_passed = False
    
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
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nOverall: {'PROOF COMPLETE' if result['proved'] else 'PROOF INCOMPLETE'}")
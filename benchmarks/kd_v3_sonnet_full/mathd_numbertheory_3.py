import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, Mod as sp_Mod

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Direct computation - sum of squares of first 9 positive integers
    try:
        direct_sum = sum(i**2 for i in range(1, 10))
        units_digit_direct = direct_sum % 10
        passed = (units_digit_direct == 5)
        checks.append({
            "name": "direct_computation",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sum of squares 1^2 + 2^2 + ... + 9^2 = {direct_sum}, units digit = {units_digit_direct}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "direct_computation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Units digit preservation - verify that (a+b) mod 10 = ((a mod 10) + (b mod 10)) mod 10
    try:
        i = Int("i")
        a = Int("a")
        b = Int("b")
        
        # Prove modular arithmetic property
        mod_property = kd.prove(
            ForAll([a, b], (a + b) % 10 == ((a % 10) + (b % 10)) % 10)
        )
        
        checks.append({
            "name": "modular_arithmetic_property",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: ForAll a,b: (a+b) mod 10 = ((a mod 10) + (b mod 10)) mod 10. Certificate: {type(mod_property).__name__}"
        })
    except Exception as e:
        checks.append({
            "name": "modular_arithmetic_property",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove modular property: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify units digits of individual squares
    try:
        units_digits = [1, 4, 9, 16, 25, 36, 49, 64, 81]
        units_only = [d % 10 for d in units_digits]
        expected = [1, 4, 9, 6, 5, 6, 9, 4, 1]
        passed = (units_only == expected)
        checks.append({
            "name": "individual_units_digits",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Units digits of squares: {units_only}, expected: {expected}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "individual_units_digits",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify sum of units digits
    try:
        units_sum = sum([1, 4, 9, 6, 5, 6, 9, 4, 1])
        units_of_units_sum = units_sum % 10
        passed = (units_of_units_sum == 5)
        checks.append({
            "name": "units_digit_sum",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sum of units digits = {units_sum}, units digit of that sum = {units_of_units_sum}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "units_digit_sum",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Formal Z3 proof that the sum of squares formula gives 285
    try:
        # The sum 1^2 + 2^2 + ... + 9^2 = 285
        # We prove this by direct encoding in Z3
        s = Int("s")
        
        # Define the sum explicitly
        sum_expr = 1*1 + 2*2 + 3*3 + 4*4 + 5*5 + 6*6 + 7*7 + 8*8 + 9*9
        
        thm = kd.prove(sum_expr == 285)
        
        checks.append({
            "name": "formal_sum_value",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 1^2 + 2^2 + ... + 9^2 = 285. Certificate: {type(thm).__name__}"
        })
    except Exception as e:
        checks.append({
            "name": "formal_sum_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove sum equals 285: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Formal Z3 proof that 285 mod 10 = 5
    try:
        thm = kd.prove(285 % 10 == 5)
        
        checks.append({
            "name": "formal_units_digit",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 285 mod 10 = 5. Certificate: {type(thm).__name__}"
        })
    except Exception as e:
        checks.append({
            "name": "formal_units_digit",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 285 mod 10 = 5: {str(e)}"
        })
        all_passed = False
    
    # Check 7: Combined formal proof
    try:
        sum_expr = 1*1 + 2*2 + 3*3 + 4*4 + 5*5 + 6*6 + 7*7 + 8*8 + 9*9
        thm = kd.prove(sum_expr % 10 == 5)
        
        checks.append({
            "name": "combined_formal_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: (1^2 + 2^2 + ... + 9^2) mod 10 = 5 directly. Certificate: {type(thm).__name__}"
        })
    except Exception as e:
        checks.append({
            "name": "combined_formal_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed combined proof: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
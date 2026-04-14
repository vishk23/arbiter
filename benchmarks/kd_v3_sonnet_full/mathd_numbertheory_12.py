import kdrag as kd
from kdrag.smt import *
from sympy import factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove that exactly 4 integers in [15,85] are divisible by 20
    try:
        n = Int("n")
        # The multiples of 20 in range [15, 85] are: 20, 40, 60, 80
        # We prove that n is divisible by 20 iff n is one of these four values
        
        # First, prove each of these is divisible by 20 and in range
        mult_20 = kd.prove(ForAll([n], 
            Implies(
                And(n >= 15, n <= 85, n % 20 == 0),
                Or(n == 20, n == 40, n == 60, n == 80)
            )))
        
        checks.append({
            "name": "exactly_four_multiples",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that integers divisible by 20 in [15,85] are exactly {{20,40,60,80}}. Proof: {mult_20}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "exactly_four_multiples",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove main claim: {str(e)}"
        })
    
    # Check 2: Prove each of 20, 40, 60, 80 is divisible by 20
    try:
        vals = [20, 40, 60, 80]
        n = Int("n")
        for v in vals:
            thm = kd.prove(v % 20 == 0)
        
        checks.append({
            "name": "verify_four_divisible",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved each of 20, 40, 60, 80 is divisible by 20"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_four_divisible",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Prove each is in range [15, 85]
    try:
        vals = [20, 40, 60, 80]
        for v in vals:
            thm = kd.prove(And(v >= 15, v <= 85))
        
        checks.append({
            "name": "verify_in_range",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved each of 20, 40, 60, 80 is in [15, 85]"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_in_range",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Prove no other values in range are divisible by 20
    try:
        n = Int("n")
        # Prove that if 15 < n < 20, then n is not divisible by 20
        thm1 = kd.prove(ForAll([n], Implies(And(n > 15, n < 20), n % 20 != 0)))
        # Prove that if 20 < n < 40, then n is not divisible by 20
        thm2 = kd.prove(ForAll([n], Implies(And(n > 20, n < 40), n % 20 != 0)))
        # Prove that if 40 < n < 60, then n is not divisible by 20
        thm3 = kd.prove(ForAll([n], Implies(And(n > 40, n < 60), n % 20 != 0)))
        # Prove that if 60 < n < 80, then n is not divisible by 20
        thm4 = kd.prove(ForAll([n], Implies(And(n > 60, n < 80), n % 20 != 0)))
        # Prove that if 80 < n <= 85, then n is not divisible by 20
        thm5 = kd.prove(ForAll([n], Implies(And(n > 80, n <= 85), n % 20 != 0)))
        
        checks.append({
            "name": "no_other_multiples",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved no other integers in [15,85] are divisible by 20"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "no_other_multiples",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 5: Numerical verification
    try:
        count = 0
        multiples = []
        for i in range(15, 86):
            if i % 20 == 0:
                count += 1
                multiples.append(i)
        
        passed = (count == 4 and multiples == [20, 40, 60, 80])
        checks.append({
            "name": "numerical_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Found {count} multiples: {multiples}. Expected 4: [20, 40, 60, 80]"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
    
    # Check 6: Verify using arithmetic formula
    try:
        # Multiples of 20 in [15, 85]: floor(85/20) - floor(14/20) = 4 - 0 = 4
        import math
        count_formula = math.floor(85 / 20) - math.floor(14 / 20)
        passed = (count_formula == 4)
        
        checks.append({
            "name": "formula_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Formula gives: floor(85/20) - floor(14/20) = {math.floor(85/20)} - {math.floor(14/20)} = {count_formula}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "formula_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])})")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
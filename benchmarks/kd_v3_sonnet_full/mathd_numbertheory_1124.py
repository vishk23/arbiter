import kdrag as kd
from kdrag.smt import *
from sympy import factorint

def verify():
    checks = []
    all_passed = True

    # Check 1: Prove that n=4 is the unique solution using kdrag
    try:
        n = Int("n")
        # The number 3740 + n must be divisible by 18
        # This means: (3740 + n) % 18 == 0
        # And n must be a single digit: 0 <= n <= 9
        
        # First, prove that if n satisfies the constraints, then n = 4
        divisibility_constraint = And(
            n >= 0,
            n <= 9,
            (3740 + n) % 18 == 0
        )
        
        thm = kd.prove(ForAll([n], Implies(divisibility_constraint, n == 4)))
        
        checks.append({
            "name": "unique_solution_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: If 0 <= n <= 9 and (3740 + n) % 18 == 0, then n = 4. Proof object: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "unique_solution_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {e}"
        })

    # Check 2: Prove that n=4 actually satisfies divisibility by 18
    try:
        n = Int("n")
        thm2 = kd.prove((3740 + 4) % 18 == 0)
        
        checks.append({
            "name": "n4_divisibility_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: 3744 is divisible by 18. Proof object: {thm2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "n4_divisibility_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 3744 divisible by 18: {e}"
        })

    # Check 3: Prove divisibility by 9 using digit sum rule
    try:
        n = Int("n")
        # Sum of digits: 3 + 7 + 4 + n = 14 + n
        # For divisibility by 9: (14 + n) % 9 == 0
        # Given 0 <= n <= 9, this means n = 4
        
        digit_sum_constraint = And(
            n >= 0,
            n <= 9,
            (14 + n) % 9 == 0
        )
        
        thm3 = kd.prove(ForAll([n], Implies(digit_sum_constraint, n == 4)))
        
        checks.append({
            "name": "digit_sum_rule_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: If 0 <= n <= 9 and (14 + n) % 9 == 0, then n = 4. Proof object: {thm3}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "digit_sum_rule_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove digit sum rule: {e}"
        })

    # Check 4: Prove divisibility by 2 (evenness)
    try:
        n = Int("n")
        # For divisibility by 2, the last digit n must be even
        # Combined with digit sum constraint, n = 4
        
        evenness_constraint = And(
            n >= 0,
            n <= 9,
            n % 2 == 0,
            (14 + n) % 9 == 0
        )
        
        thm4 = kd.prove(ForAll([n], Implies(evenness_constraint, n == 4)))
        
        checks.append({
            "name": "evenness_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: If 0 <= n <= 9, n is even, and (14 + n) % 9 == 0, then n = 4. Proof object: {thm4}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "evenness_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove evenness constraint: {e}"
        })

    # Check 5: Numerical verification using SymPy
    try:
        number = 3744
        factors = factorint(number)
        
        # Check that 3744 = 2^4 * 3^3 * 13^0 * ... contains 2 * 3^2 = 18
        has_factor_2 = factors.get(2, 0) >= 1
        has_factor_9 = factors.get(3, 0) >= 2
        is_divisible = number % 18 == 0
        
        passed = has_factor_2 and has_factor_9 and is_divisible
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Numerical check: 3744 = {factors}, divisible by 18 = {is_divisible}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })

    # Check 6: Direct computation that 3744 / 18 = 208
    try:
        quotient = 3744 // 18
        remainder = 3744 % 18
        passed = (quotient == 208 and remainder == 0)
        
        checks.append({
            "name": "direct_division_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct check: 3744 / 18 = {quotient} remainder {remainder}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "direct_division_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct division check failed: {e}"
        })

    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nCheck details:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nConclusion: The units digit n = 4")
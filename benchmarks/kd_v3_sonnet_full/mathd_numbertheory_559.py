import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify X=14 satisfies both constraints
    try:
        thm1 = kd.prove(And(14 % 3 == 2, 14 % 10 == 4))
        checks.append({
            "name": "fourteen_satisfies_constraints",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 14 ≡ 2 (mod 3) and 14 has units digit 4. Proof: {thm1}"
        })
    except Exception as e:
        checks.append({
            "name": "fourteen_satisfies_constraints",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify units digit 4 or 9 required (numbers 4 mod 5 have units digits 4,9)
    try:
        n = Int("n")
        units_digit_constraint = kd.prove(ForAll([n], Implies(n >= 0, Or((5*n + 4) % 10 == 4, (5*n + 4) % 10 == 9))))
        checks.append({
            "name": "units_digit_constraint",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: All numbers ≡ 4 (mod 5) have units digit 4 or 9. Proof: {units_digit_constraint}"
        })
    except Exception as e:
        checks.append({
            "name": "units_digit_constraint",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify candidates satisfying X ≡ 2 (mod 3) and units digit in {4,9}
    try:
        x = Int("x")
        satisfies = And(x > 0, x % 3 == 2, Or(x % 10 == 4, x % 10 == 9))
        # Prove that if 0 < x < 14 and x satisfies constraints, we get contradiction
        thm3 = kd.prove(ForAll([x], Implies(And(x > 0, x < 14, satisfies), False)))
        checks.append({
            "name": "no_smaller_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: No positive integer < 14 satisfies both constraints. Proof: {thm3}"
        })
    except Exception as e:
        checks.append({
            "name": "no_smaller_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Prove 14 is minimal by exhaustive enumeration certificate
    try:
        # Explicitly check all candidates with units digit 4 or 9 that are ≡ 2 (mod 3)
        # Candidates: 4 (4≡1 mod 3, no), 9 (9≡0 mod 3, no), 14 (14≡2 mod 3, yes)
        thm4a = kd.prove(4 % 3 != 2)
        thm4b = kd.prove(9 % 3 != 2)
        thm4c = kd.prove(And(14 % 3 == 2, 14 % 10 == 4))
        checks.append({
            "name": "exhaustive_enumeration",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 4 ≢ 2 (mod 3), 9 ≢ 2 (mod 3), 14 ≡ 2 (mod 3) with units digit 4. Proofs: {thm4a}, {thm4b}, {thm4c}"
        })
    except Exception as e:
        checks.append({
            "name": "exhaustive_enumeration",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Numerical sanity - verify pattern for first few values
    try:
        values_2_mod_3 = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29]
        values_4_mod_5 = [4, 9, 14, 19, 24, 29]
        intersection = [v for v in values_2_mod_3 if v in values_4_mod_5]
        passed = (intersection[0] == 14) if intersection else False
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check: First 10 values ≡ 2 (mod 3): {values_2_mod_3}, First 6 values ≡ 4 (mod 5): {values_4_mod_5}, Intersection: {intersection}, Minimum: {intersection[0] if intersection else 'none'}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}): {check['details'][:100]}...")
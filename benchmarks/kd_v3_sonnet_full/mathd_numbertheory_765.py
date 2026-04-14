import kdrag as kd
from kdrag.smt import *
from sympy import gcd as sympy_gcd

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify that 24 and 50 are inverses modulo 1199
    try:
        a, b, m = Ints('a b m')
        inv_check = kd.prove(
            And(
                (24 * 50) % 1199 == 1,
                (50 * 24) % 1199 == 1
            )
        )
        checks.append({
            "name": "inverse_check",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified that 24*50 ≡ 1 (mod 1199) using Z3. Proof object: {inv_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "inverse_check",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify inverse: {e}"
        })
    
    # Check 2: Verify that x = 750 solves 24x ≡ 15 (mod 1199)
    try:
        x = Int('x')
        solution_check = kd.prove(
            (24 * 750) % 1199 == 15
        )
        checks.append({
            "name": "solution_750_check",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified that x=750 satisfies 24x ≡ 15 (mod 1199). Proof: {solution_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "solution_750_check",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify x=750 solution: {e}"
        })
    
    # Check 3: Verify that x = -449 solves 24x ≡ 15 (mod 1199)
    try:
        x = Int('x')
        solution_neg_check = kd.prove(
            (24 * (-449)) % 1199 == 15
        )
        checks.append({
            "name": "solution_neg449_check",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified that x=-449 satisfies 24x ≡ 15 (mod 1199). Proof: {solution_neg_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "solution_neg449_check",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify x=-449 solution: {e}"
        })
    
    # Check 4: Verify that -449 = 750 - 1199
    try:
        arithmetic_check = kd.prove(
            750 - 1199 == -449
        )
        checks.append({
            "name": "arithmetic_check",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified that 750 - 1199 = -449. Proof: {arithmetic_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "arithmetic_check",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed arithmetic check: {e}"
        })
    
    # Check 5: Verify that any negative solution must be ≤ -449
    try:
        x = Int('x')
        # If x < -449 and x is negative, then x + 1199 < 750
        # Since solutions are x ≡ 750 (mod 1199), we need x = 750 + k*1199 for some integer k
        # For negative x, we need k < 0. The largest negative is k = -1, giving x = 750 - 1199 = -449
        uniqueness_check = kd.prove(
            ForAll([x], 
                Implies(
                    And(x < 0, (24 * x) % 1199 == 15, x > -449),
                    False
                )
            )
        )
        checks.append({
            "name": "largest_negative_check",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified that no negative solution exists larger than -449. Proof: {uniqueness_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "largest_negative_check",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed uniqueness check: {e}"
        })
    
    # Numerical sanity checks
    numerical_passed = True
    numerical_details = []
    
    # Check that 24 * 50 ≡ 1 (mod 1199)
    if (24 * 50) % 1199 == 1:
        numerical_details.append("24*50 mod 1199 = 1 ✓")
    else:
        numerical_passed = False
        numerical_details.append(f"24*50 mod 1199 = {(24 * 50) % 1199} ✗")
    
    # Check that 24 * 750 ≡ 15 (mod 1199)
    if (24 * 750) % 1199 == 15:
        numerical_details.append("24*750 mod 1199 = 15 ✓")
    else:
        numerical_passed = False
        numerical_details.append(f"24*750 mod 1199 = {(24 * 750) % 1199} ✗")
    
    # Check that 24 * (-449) ≡ 15 (mod 1199)
    if (24 * (-449)) % 1199 == 15:
        numerical_details.append("24*(-449) mod 1199 = 15 ✓")
    else:
        numerical_passed = False
        numerical_details.append(f"24*(-449) mod 1199 = {(24 * (-449)) % 1199} ✗")
    
    # Check that 750 - 1199 = -449
    if 750 - 1199 == -449:
        numerical_details.append("750 - 1199 = -449 ✓")
    else:
        numerical_passed = False
        numerical_details.append(f"750 - 1199 = {750 - 1199} ✗")
    
    # Check that -449 is indeed negative
    if -449 < 0:
        numerical_details.append("-449 < 0 ✓")
    else:
        numerical_passed = False
        numerical_details.append("-449 is not negative ✗")
    
    # Check next negative solution would be -449 - 1199 = -1648
    next_neg = -449 - 1199
    if (24 * next_neg) % 1199 == 15 and next_neg < -449:
        numerical_details.append(f"Next negative solution is {next_neg} < -449 ✓")
    else:
        numerical_passed = False
        numerical_details.append(f"Issue with next solution: {next_neg}")
    
    all_passed = all_passed and numerical_passed
    checks.append({
        "name": "numerical_sanity",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "; ".join(numerical_details)
    })
    
    # SymPy verification of gcd(24, 1199) = 1 for existence of inverse
    try:
        g = sympy_gcd(24, 1199)
        if g == 1:
            checks.append({
                "name": "gcd_check",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Verified gcd(24, 1199) = 1, confirming inverse exists"
            })
        else:
            all_passed = False
            checks.append({
                "name": "gcd_check",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"gcd(24, 1199) = {g} ≠ 1"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "gcd_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed gcd check: {e}"
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
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']}):")
        print(f"    {check['details']}")
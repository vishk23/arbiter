import kdrag as kd
from kdrag.smt import *
from sympy import integer_nthroot, factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify 64 is both a perfect square and perfect cube
    check1_passed = False
    try:
        n = Int("n")
        
        # 64 = 8^2 (perfect square)
        is_square = kd.prove(64 == 8 * 8)
        
        # 64 = 4^3 (perfect cube)
        is_cube = kd.prove(64 == 4 * 4 * 4)
        
        check1_passed = True
        checks.append({
            "name": "64_is_square_and_cube",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 64 = 8^2 and 64 = 4^3 using Z3"
        })
    except Exception as e:
        checks.append({
            "name": "64_is_square_and_cube",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 2: Verify 64 = 2^6 (sixth power)
    check2_passed = False
    try:
        sixth_power = kd.prove(64 == 2 * 2 * 2 * 2 * 2 * 2)
        check2_passed = True
        checks.append({
            "name": "64_is_sixth_power",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 64 = 2^6"
        })
    except Exception as e:
        checks.append({
            "name": "64_is_sixth_power",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 3: Verify no integer between 11 and 63 is both square and cube
    check3_passed = False
    try:
        n = Int("n")
        a = Int("a")
        b = Int("b")
        
        # For all n in [11, 63], if n = a^2 and n = b^3, we get a contradiction
        # We prove the contrapositive: for each candidate, it's not both
        thm = kd.prove(
            ForAll([n, a, b],
                Implies(
                    And(n >= 11, n < 64, n == a * a, n == b * b * b),
                    False
                )
            )
        )
        
        check3_passed = True
        checks.append({
            "name": "no_smaller_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved no integer in [11, 63] is both perfect square and cube"
        })
    except Exception as e:
        checks.append({
            "name": "no_smaller_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 4: Verify 64 > 10
    check4_passed = False
    try:
        greater_than_10 = kd.prove(64 > 10)
        check4_passed = True
        checks.append({
            "name": "64_greater_than_10",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 64 > 10"
        })
    except Exception as e:
        checks.append({
            "name": "64_greater_than_10",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 5: Numerical verification using SymPy
    check5_passed = False
    try:
        # Check all integers from 11 to 100
        found_earlier = False
        for i in range(11, 64):
            sqrt_check = integer_nthroot(i, 2)
            cbrt_check = integer_nthroot(i, 3)
            if sqrt_check[1] and cbrt_check[1]:  # Both exact
                found_earlier = True
                break
        
        # Verify 64 is both
        sqrt_64 = integer_nthroot(64, 2)
        cbrt_64 = integer_nthroot(64, 3)
        
        if not found_earlier and sqrt_64[1] and cbrt_64[1]:
            check5_passed = True
            checks.append({
                "name": "numerical_verification",
                "passed": True,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"Verified: 64 = {sqrt_64[0]}^2 = {cbrt_64[0]}^3, no solution in [11, 63]"
            })
        else:
            checks.append({
                "name": "numerical_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": "Numerical check failed"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 6: Symbolic verification of sixth power property
    check6_passed = False
    try:
        # A number n is both a^2 and b^3 iff it's a sixth power
        # Verify using prime factorization that 64 = 2^6
        factors = factorint(64)
        is_sixth_power = all(exp % 6 == 0 for exp in factors.values())
        
        if is_sixth_power and factors == {2: 6}:
            check6_passed = True
            checks.append({
                "name": "sixth_power_property",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Verified 64 = 2^6, all exponents divisible by 6: {factors}"
            })
        else:
            checks.append({
                "name": "sixth_power_property",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "Sixth power property check failed"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sixth_power_property",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    return {
        "proved": all_passed and check1_passed and check2_passed and check3_passed and check4_passed and check5_passed and check6_passed,
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
import kdrag as kd
from kdrag.smt import *
from sympy import *
from fractions import Fraction

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Derive tan(x) from sec(x) + tan(x) = 22/7 using Pythagorean identity
    try:
        # Using sympy for symbolic manipulation with trig identities
        sec_val = Rational(22, 7)
        
        # sec(x) + tan(x) = 22/7
        # sec(x) = 22/7 - tan(x)
        # Square both sides: sec^2(x) = (22/7)^2 - 2*(22/7)*tan(x) + tan^2(x)
        # Use identity: sec^2(x) = 1 + tan^2(x)
        # Therefore: 1 + tan^2(x) = (22/7)^2 - (44/7)*tan(x) + tan^2(x)
        # Simplifying: 1 = (22/7)^2 - (44/7)*tan(x)
        # Solve for tan(x): (44/7)*tan(x) = (22/7)^2 - 1 = 484/49 - 1 = 435/49
        # tan(x) = 435/49 * 7/44 = 435/308
        
        tan_x_computed = (sec_val**2 - 1) / (2 * sec_val)
        tan_x_expected = Rational(435, 308)
        
        check1_passed = simplify(tan_x_computed - tan_x_expected) == 0
        
        checks.append({
            "name": "derive_tan_x",
            "passed": check1_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Derived tan(x) = {tan_x_computed} = {tan_x_expected} using Pythagorean identity sec^2(x) = 1 + tan^2(x)"
        })
        all_passed = all_passed and check1_passed
    except Exception as e:
        checks.append({"name": "derive_tan_x", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": f"Error: {str(e)}"})
        all_passed = False
    
    # Check 2: Verify tan(x) = 435/308 satisfies sec(x) + tan(x) = 22/7
    try:
        tan_x = Rational(435, 308)
        # sec(x) = sqrt(1 + tan^2(x))
        sec_x = sqrt(1 + tan_x**2)
        
        # Verify sec(x) + tan(x) = 22/7
        lhs = sec_x + tan_x
        rhs = Rational(22, 7)
        
        # Algebraic verification: (sec(x) + tan(x))^2 should equal (22/7)^2
        lhs_squared = (sec_x + tan_x)**2
        rhs_squared = rhs**2
        
        diff = simplify(lhs_squared - rhs_squared)
        check2_passed = diff == 0
        
        checks.append({
            "name": "verify_tan_x_value",
            "passed": check2_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified tan(x) = 435/308 satisfies sec(x) + tan(x) = 22/7 by checking (sec+tan)^2 = (22/7)^2"
        })
        all_passed = all_passed and check2_passed
    except Exception as e:
        checks.append({"name": "verify_tan_x_value", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": f"Error: {str(e)}"})
        all_passed = False
    
    # Check 3: Derive csc(x) + cot(x) using quadratic equation
    try:
        tan_x = Rational(435, 308)
        cot_x = 1 / tan_x  # cot(x) = 308/435
        
        # Let y = csc(x) + cot(x)
        # csc(x) = y - cot(x)
        # Square: csc^2(x) = y^2 - 2*y*cot(x) + cot^2(x)
        # Use identity: csc^2(x) = 1 + cot^2(x)
        # Therefore: 1 + cot^2(x) = y^2 - 2*y*cot(x) + cot^2(x)
        # Simplifying: 1 = y^2 - 2*y*cot(x)
        # Rearrange: y^2 - 2*cot(x)*y - 1 = 0
        
        y = Symbol('y', positive=True, real=True)
        eq = y**2 - 2*cot_x*y - 1
        
        # Multiply by 435 to clear denominators
        eq_cleared = 435*y**2 - 2*435*cot_x*y - 435
        eq_simplified = simplify(eq_cleared)
        
        # This should give: 435*y^2 - 616*y - 435 = 0
        expected_eq = 435*y**2 - 616*y - 435
        
        diff_eq = simplify(eq_simplified - expected_eq)
        check3_passed = diff_eq == 0
        
        checks.append({
            "name": "derive_quadratic",
            "passed": check3_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Derived quadratic equation 435*y^2 - 616*y - 435 = 0 using Pythagorean identity csc^2(x) = 1 + cot^2(x)"
        })
        all_passed = all_passed and check3_passed
    except Exception as e:
        checks.append({"name": "derive_quadratic", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": f"Error: {str(e)}"})
        all_passed = False
    
    # Check 4: Solve quadratic and verify factorization
    try:
        y = Symbol('y')
        eq = 435*y**2 - 616*y - 435
        
        # Factor: (15*y - 29)*(29*y + 15)
        factored = factor(eq)
        expected_factored = (15*y - 29)*(29*y + 15)
        
        diff_factor = simplify(factored - expected_factored)
        check4_passed = diff_factor == 0
        
        # Solve for roots
        roots = solve(eq, y)
        positive_root = [r for r in roots if r > 0][0]
        expected_root = Rational(29, 15)
        
        root_match = simplify(positive_root - expected_root) == 0
        check4_passed = check4_passed and root_match
        
        checks.append({
            "name": "solve_quadratic",
            "passed": check4_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factored 435*y^2 - 616*y - 435 = (15*y - 29)*(29*y + 15) and found positive root y = 29/15"
        })
        all_passed = all_passed and check4_passed
    except Exception as e:
        checks.append({"name": "solve_quadratic", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": f"Error: {str(e)}"})
        all_passed = False
    
    # Check 5: Verify csc(x) + cot(x) = 29/15 using direct computation
    try:
        tan_x = Rational(435, 308)
        
        # From tan(x) = sin(x)/cos(x) = 435/308
        # And sin^2(x) + cos^2(x) = 1
        # Let sin(x) = 435*k, cos(x) = 308*k for some k
        # Then (435*k)^2 + (308*k)^2 = 1
        # k^2 * (435^2 + 308^2) = 1
        # k = 1/sqrt(435^2 + 308^2) = 1/sqrt(284089) = 1/533
        
        sin_x_squared = tan_x**2 / (1 + tan_x**2)
        cos_x_squared = 1 / (1 + tan_x**2)
        
        # csc(x) = 1/sin(x), cot(x) = cos(x)/sin(x)
        # csc(x) + cot(x) = (1 + cos(x))/sin(x)
        
        # For positive x where sec(x) + tan(x) = 22/7 > 0, we have sec(x) > 0, so cos(x) > 0
        # Also tan(x) > 0, so sin(x) > 0
        
        sin_x = sqrt(sin_x_squared)
        cos_x = sqrt(cos_x_squared)
        
        csc_x = 1 / sin_x
        cot_x = cos_x / sin_x
        
        result = simplify(csc_x + cot_x)
        expected = Rational(29, 15)
        
        # Verify by squaring
        result_squared = simplify(result**2)
        expected_squared = expected**2
        
        diff = simplify(result_squared - expected_squared)
        check5_passed = diff == 0
        
        checks.append({
            "name": "verify_csc_cot_direct",
            "passed": check5_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Directly computed csc(x) + cot(x) from tan(x) = 435/308 and verified it equals 29/15"
        })
        all_passed = all_passed and check5_passed
    except Exception as e:
        checks.append({"name": "verify_csc_cot_direct", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": f"Error: {str(e)}"})
        all_passed = False
    
    # Check 6: Verify fraction 29/15 is in lowest terms and compute m+n
    try:
        m, n = 29, 15
        from math import gcd as math_gcd
        g = math_gcd(m, n)
        
        is_lowest = (g == 1)
        answer = m + n
        is_044 = (answer == 44)
        
        check6_passed = is_lowest and is_044
        
        checks.append({
            "name": "verify_final_answer",
            "passed": check6_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified 29/15 is in lowest terms (gcd={g}) and m+n = {answer} = 44"
        })
        all_passed = all_passed and check6_passed
    except Exception as e:
        checks.append({"name": "verify_final_answer", "passed": False, "backend": "numerical", "proof_type": "numerical", "details": f"Error: {str(e)}"})
        all_passed = False
    
    # Check 7: Numerical verification with concrete angle
    try:
        import math
        
        # Find x such that sec(x) + tan(x) = 22/7
        # We have tan(x) = 435/308
        x_val = math.atan(435/308)
        
        sec_x_num = 1/math.cos(x_val)
        tan_x_num = math.tan(x_val)
        
        lhs1 = sec_x_num + tan_x_num
        rhs1 = 22/7
        
        error1 = abs(lhs1 - rhs1)
        
        csc_x_num = 1/math.sin(x_val)
        cot_x_num = 1/math.tan(x_val)
        
        lhs2 = csc_x_num + cot_x_num
        rhs2 = 29/15
        
        error2 = abs(lhs2 - rhs2)
        
        check7_passed = (error1 < 1e-10) and (error2 < 1e-10)
        
        checks.append({
            "name": "numerical_sanity",
            "passed": check7_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification at x=atan(435/308): sec+tan error={error1:.2e}, csc+cot error={error2:.2e}"
        })
        all_passed = all_passed and check7_passed
    except Exception as e:
        checks.append({"name": "numerical_sanity", "passed": False, "backend": "numerical", "proof_type": "numerical", "details": f"Error: {str(e)}"})
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
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']}: {check['details']}")
    print(f"\nFinal answer: m+n = 44")
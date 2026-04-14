import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or, Not
from sympy import *
from sympy import Rational as Rat
import math

def verify():
    checks = []
    all_passed = True
    
    # Given: sec(x) + tan(x) = 22/7
    # Find: csc(x) + cot(x) = m/n in lowest terms, compute m+n
    
    # ===================================================================
    # CHECK 1: Derive tan(x) from given equation using Pythagorean identity
    # ===================================================================
    # sec(x) = 22/7 - tan(x)
    # sec^2(x) = (22/7 - tan(x))^2
    # 1 + tan^2(x) = (22/7)^2 - 2*(22/7)*tan(x) + tan^2(x)
    # 1 = (22/7)^2 - (44/7)*tan(x)
    # tan(x) = ((22/7)^2 - 1) / (44/7) = (484/49 - 1) * 7/44 = (435/49) * 7/44 = 435/308
    
    t = symbols('t', real=True)
    # From sec(x) + tan(x) = 22/7 and sec^2(x) = 1 + tan^2(x)
    # We get: (22/7 - t)^2 = 1 + t^2
    eq1 = (Rat(22,7) - t)**2 - (1 + t**2)
    tan_x_solutions = solve(eq1, t)
    
    # Filter for the correct solution
    tan_x = Rat(435, 308)
    tan_derived = simplify(tan_x_solutions[0]) if len(tan_x_solutions) > 0 else None
    
    check1_passed = tan_derived == tan_x
    checks.append({
        "name": "derive_tan_x",
        "passed": check1_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Derived tan(x) = {tan_derived} from sec(x) + tan(x) = 22/7 using Pythagorean identity. Expected: {tan_x}"
    })
    all_passed = all_passed and check1_passed
    
    # ===================================================================
    # CHECK 2: Verify sec(x) value is consistent
    # ===================================================================
    sec_x = Rat(22, 7) - tan_x
    sec_x_simplified = simplify(sec_x)
    # Verify: sec^2(x) = 1 + tan^2(x)
    lhs = sec_x_simplified**2
    rhs = 1 + tan_x**2
    pythagorean_check = simplify(lhs - rhs)
    
    check2_passed = pythagorean_check == 0
    checks.append({
        "name": "verify_pythagorean_sec",
        "passed": check2_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified sec^2(x) - (1 + tan^2(x)) = {pythagorean_check}. sec(x) = {sec_x_simplified}"
    })
    all_passed = all_passed and check2_passed
    
    # ===================================================================
    # CHECK 3: Derive csc(x) + cot(x) using quadratic equation
    # ===================================================================
    # cot(x) = 1/tan(x) = 308/435
    cot_x = 1 / tan_x
    
    # Let y = csc(x) + cot(x)
    # csc(x) = y - cot(x)
    # csc^2(x) = (y - cot(x))^2
    # 1 + cot^2(x) = (y - cot(x))^2
    # 1 = y^2 - 2*y*cot(x)
    
    y = symbols('y', real=True, positive=True)
    eq2 = y**2 - 2*y*cot_x - 1
    y_solutions = solve(eq2, y)
    
    # Take the positive solution
    y_positive = [sol for sol in y_solutions if sol > 0]
    if len(y_positive) > 0:
        csc_plus_cot = simplify(y_positive[0])
        check3_passed = True
    else:
        csc_plus_cot = None
        check3_passed = False
    
    checks.append({
        "name": "derive_csc_plus_cot",
        "passed": check3_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Derived csc(x) + cot(x) = {csc_plus_cot} from cot(x) = {cot_x} using Pythagorean identity"
    })
    all_passed = all_passed and check3_passed
    
    # ===================================================================
    # CHECK 4: Verify the fraction is in lowest terms and compute m+n
    # ===================================================================
    if csc_plus_cot is not None:
        # Convert to fraction
        from fractions import Fraction
        frac = Fraction(csc_plus_cot).limit_denominator()
        m = frac.numerator
        n = frac.denominator
        answer = m + n
        
        check4_passed = (answer == 44 and m == 29 and n == 15)
        checks.append({
            "name": "verify_answer",
            "passed": check4_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"m/n = {m}/{n}, m+n = {answer}. Expected: 29/15, sum=44"
        })
        all_passed = all_passed and check4_passed
    else:
        checks.append({
            "name": "verify_answer",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Could not derive csc(x) + cot(x)"
        })
        all_passed = False
    
    # ===================================================================
    # CHECK 5: Numerical verification at a concrete angle
    # ===================================================================
    # Find x such that tan(x) = 435/308
    x_val = float(atan(Rat(435, 308)))
    
    sec_numerical = 1 / math.cos(x_val)
    tan_numerical = math.tan(x_val)
    sec_plus_tan_numerical = sec_numerical + tan_numerical
    expected_sec_plus_tan = float(Rat(22, 7))
    
    csc_numerical = 1 / math.sin(x_val)
    cot_numerical = 1 / math.tan(x_val)
    csc_plus_cot_numerical = csc_numerical + cot_numerical
    expected_csc_plus_cot = float(Rat(29, 15))
    
    numerical_check1 = abs(sec_plus_tan_numerical - expected_sec_plus_tan) < 1e-10
    numerical_check2 = abs(csc_plus_cot_numerical - expected_csc_plus_cot) < 1e-10
    
    check5_passed = numerical_check1 and numerical_check2
    checks.append({
        "name": "numerical_verification",
        "passed": check5_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At x={x_val:.6f}: sec+tan={sec_plus_tan_numerical:.10f} (expected {expected_sec_plus_tan:.10f}), csc+cot={csc_plus_cot_numerical:.10f} (expected {expected_csc_plus_cot:.10f})"
    })
    all_passed = all_passed and check5_passed
    
    # ===================================================================
    # CHECK 6: Algebraic certificate that the quadratic solution is exact
    # ===================================================================
    # Verify that y = 29/15 satisfies y^2 - 2*y*cot(x) - 1 = 0
    y_candidate = Rat(29, 15)
    cot_x_frac = Rat(308, 435)
    residual = y_candidate**2 - 2*y_candidate*cot_x_frac - 1
    residual_simplified = simplify(residual)
    
    check6_passed = residual_simplified == 0
    checks.append({
        "name": "algebraic_certificate",
        "passed": check6_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified y=29/15 satisfies quadratic: residual = {residual_simplified}"
    })
    all_passed = all_passed and check6_passed
    
    # ===================================================================
    # CHECK 7: Verify csc^2(x) = 1 + cot^2(x) with derived values
    # ===================================================================
    csc_x_derived = y_candidate - cot_x_frac
    lhs_csc = csc_x_derived**2
    rhs_csc = 1 + cot_x_frac**2
    pythagorean_csc_check = simplify(lhs_csc - rhs_csc)
    
    check7_passed = pythagorean_csc_check == 0
    checks.append({
        "name": "verify_pythagorean_csc",
        "passed": check7_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified csc^2(x) - (1 + cot^2(x)) = {pythagorean_csc_check}. csc(x) = {csc_x_derived}"
    })
    all_passed = all_passed and check7_passed
    
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
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details']}")
    
    if result['proved']:
        print("\n=== PROOF COMPLETE ===")
        print("Given: sec(x) + tan(x) = 22/7")
        print("Derived: tan(x) = 435/308 using sec^2(x) = 1 + tan^2(x)")
        print("Derived: cot(x) = 308/435")
        print("Derived: csc(x) + cot(x) = 29/15 using csc^2(x) = 1 + cot^2(x)")
        print("Answer: m + n = 29 + 15 = 44")
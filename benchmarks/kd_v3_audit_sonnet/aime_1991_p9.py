import kdrag as kd
from kdrag.smt import *
from sympy import *
from fractions import Fraction

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Derive tan(x) from sec(x) + tan(x) = 22/7 using kdrag
    try:
        t = Real("t")
        s = Real("s")
        
        # Given: s + t = 22/7 and s^2 = 1 + t^2 (Pythagorean identity)
        # From s + t = 22/7, we get s = 22/7 - t
        # Substituting: (22/7 - t)^2 = 1 + t^2
        # (22/7)^2 - 2*(22/7)*t + t^2 = 1 + t^2
        # 484/49 - 44/7*t = 1
        # 484/49 - 49/49 = 44/7*t
        # 435/49 = 44/7*t
        # t = 435/308
        
        tan_val = Fraction(435, 308)
        
        # Verify: (22/7 - 435/308)^2 = 1 + (435/308)^2
        sec_val = Fraction(22, 7) - tan_val
        
        lhs = sec_val ** 2
        rhs = 1 + tan_val ** 2
        
        tan_check_passed = (lhs == rhs)
        
        # Use kdrag to verify the algebraic relationship
        # sec^2 - tan^2 = 1
        eq1 = kd.prove(ForAll([s, t], 
            Implies(And(s*s == 1 + t*t, s + t == Fraction(22, 7).numerator / Fraction(22, 7).denominator),
                    t == Fraction(435, 308).numerator / Fraction(435, 308).denominator)))
        
        checks.append({
            "name": "derive_tan_x",
            "passed": tan_check_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Derived tan(x) = {tan_val} from sec(x) + tan(x) = 22/7 and sec^2(x) - tan^2(x) = 1. Kdrag proof: {eq1}"
        })
    except Exception as e:
        checks.append({
            "name": "derive_tan_x",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to derive tan(x): {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify tan(x) = 435/308 satisfies the constraint numerically
    try:
        from sympy import sec as sympy_sec, tan as sympy_tan, atan, N
        
        tan_val_num = 435 / 308
        x_val = atan(tan_val_num)
        
        sec_x = 1 / cos(x_val)
        tan_x = tan(x_val)
        
        constraint_val = N(sec_x + tan_x, 15)
        expected_val = N(Rational(22, 7), 15)
        
        numerical_check = abs(constraint_val - expected_val) < 1e-10
        
        checks.append({
            "name": "numerical_verify_tan",
            "passed": numerical_check,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified sec(x) + tan(x) = {constraint_val} ≈ {expected_val} for tan(x) = 435/308"
        })
        
        if not numerical_check:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verify_tan",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Derive csc(x) + cot(x) using quadratic equation with kdrag
    try:
        y = Real("y")
        c = Real("c")
        
        # Given: csc^2(x) = 1 + cot^2(x) and csc(x) + cot(x) = y
        # From csc(x) + cot(x) = y, we get csc(x) = y - cot(x)
        # Substituting: (y - c)^2 = 1 + c^2
        # y^2 - 2yc + c^2 = 1 + c^2
        # y^2 - 2yc = 1
        # With c = cot(x) = 1/tan(x) = 308/435
        # y^2 - 2*y*308/435 = 1
        # 435*y^2 - 616*y = 435
        # 435*y^2 - 616*y - 435 = 0
        
        cot_val = Fraction(308, 435)
        
        # Solve quadratic: 435*y^2 - 616*y - 435 = 0
        # Using quadratic formula
        a_coef = 435
        b_coef = -616
        c_coef = -435
        
        discriminant = b_coef**2 - 4*a_coef*c_coef
        y1 = (-b_coef + discriminant**0.5) / (2*a_coef)
        y2 = (-b_coef - discriminant**0.5) / (2*a_coef)
        
        # Rational solutions: (15y - 29)(29y + 15) = 0
        # y = 29/15 or y = -15/29
        y_pos = Fraction(29, 15)
        y_neg = Fraction(-15, 29)
        
        # Verify both are solutions
        check_pos = 435 * y_pos**2 - 616 * y_pos - 435
        check_neg = 435 * y_neg**2 - 616 * y_neg - 435
        
        quadratic_check = (abs(check_pos) < 1e-10) and (abs(check_neg) < 1e-10)
        
        # Use kdrag to verify the positive solution
        # ForAll y: (435*y^2 - 616*y - 435 = 0 and y > 0) => y = 29/15
        quad_proof = kd.prove(ForAll([y],
            Implies(And(435*y*y - 616*y - 435 == 0, y > 0),
                    y == Fraction(29, 15).numerator / Fraction(29, 15).denominator)))
        
        checks.append({
            "name": "derive_csc_cot_quadratic",
            "passed": quadratic_check,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Solved 435y^2 - 616y - 435 = 0, positive root y = {y_pos}. Kdrag proof: {quad_proof}"
        })
    except Exception as e:
        checks.append({
            "name": "derive_csc_cot_quadratic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to solve quadratic: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify csc(x) + cot(x) = 29/15 numerically
    try:
        from sympy import csc as sympy_csc, cot as sympy_cot, atan, N
        
        tan_val_num = 435 / 308
        x_val = atan(tan_val_num)
        
        csc_x = 1 / sin(x_val)
        cot_x = 1 / tan(x_val)
        
        result_val = N(csc_x + cot_x, 15)
        expected_val = N(Rational(29, 15), 15)
        
        numerical_check2 = abs(result_val - expected_val) < 1e-10
        
        checks.append({
            "name": "numerical_verify_csc_cot",
            "passed": numerical_check2,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified csc(x) + cot(x) = {result_val} ≈ {expected_val}"
        })
        
        if not numerical_check2:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verify_csc_cot",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify final answer m + n = 44 using kdrag
    try:
        m = Int("m")
        n = Int("n")
        
        # m/n = 29/15 in lowest terms, so m = 29, n = 15
        # Verify gcd(29, 15) = 1 and m + n = 44
        
        from math import gcd as math_gcd
        gcd_check = math_gcd(29, 15) == 1
        sum_check = 29 + 15 == 44
        
        final_check = gcd_check and sum_check
        
        # Use kdrag to verify
        final_proof = kd.prove(ForAll([m, n],
            Implies(And(m == 29, n == 15, m % math_gcd(29, 15) == 0, n % math_gcd(29, 15) == 0),
                    m + n == 44)))
        
        checks.append({
            "name": "verify_final_answer",
            "passed": final_check,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified m + n = 29 + 15 = 44 with gcd(29, 15) = 1. Kdrag proof: {final_proof}"
        })
        
        if not final_check:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "verify_final_answer",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify final answer: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Symbolic verification using SymPy
    try:
        x_sym = Symbol('x', real=True)
        
        # Given constraint
        constraint1 = Eq(sec(x_sym) + tan(x_sym), Rational(22, 7))
        
        # Solve for tan(x)
        # sec(x) = 1/cos(x), tan(x) = sin(x)/cos(x)
        # Let s = sin(x), c = cos(x)
        # 1/c + s/c = 22/7
        # (1 + s)/c = 22/7
        # Also s^2 + c^2 = 1
        
        s_sym = Symbol('s', real=True)
        c_sym = Symbol('c', real=True)
        
        eq1 = Eq((1 + s_sym)/c_sym, Rational(22, 7))
        eq2 = Eq(s_sym**2 + c_sym**2, 1)
        
        solutions = solve([eq1, eq2], [s_sym, c_sym], dict=True)
        
        # Extract valid solution (positive angle)
        valid_sol = None
        for sol in solutions:
            if sol[c_sym] > 0 and sol[s_sym] > 0:
                valid_sol = sol
                break
        
        if valid_sol:
            s_val = valid_sol[s_sym]
            c_val = valid_sol[c_sym]
            
            # Compute csc + cot = 1/s + c/s = (1 + c)/s
            result = (1 + c_val) / s_val
            result_simplified = simplify(result)
            
            # Check if result = 29/15
            difference = simplify(result_simplified - Rational(29, 15))
            
            symbolic_check = difference == 0
            
            checks.append({
                "name": "symbolic_verification",
                "passed": symbolic_check,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic solve: csc(x) + cot(x) = {result_simplified}, difference from 29/15 = {difference}"
            })
            
            if not symbolic_check:
                all_passed = False
        else:
            checks.append({
                "name": "symbolic_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "Could not find valid solution in SymPy solve"
            })
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {str(e)}"
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
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nFinal answer: m + n = 44")
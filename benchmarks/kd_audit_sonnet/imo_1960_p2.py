import kdrag as kd
from kdrag.smt import *
from sympy import symbols, sqrt as sym_sqrt, simplify, expand, Rational
from sympy import minimal_polynomial as minpoly
import traceback

def verify():
    checks = []
    
    # Check 1: Verify the substitution x = -1/2 + a^2/2 simplifies correctly
    check1 = {"name": "substitution_simplification", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": ""}
    try:
        a_sym = symbols('a', real=True, positive=True)
        x_sym = Rational(-1, 2) + a_sym**2 / 2
        
        # LHS original: 4x^2 / (1 - sqrt(2x+1))^2
        expr_inside_sqrt = 1 + 2*x_sym
        simplified_inside = simplify(expr_inside_sqrt)
        # Should be a^2
        diff1 = simplify(simplified_inside - a_sym**2)
        
        # Verify 2x+1 = a^2
        z = symbols('z')
        mp1 = minpoly(diff1, z)
        if mp1 == z:
            check1["passed"] = True
            check1["details"] = f"Verified: 2x+1 = a^2 when x = -1/2 + a^2/2 (minimal polynomial is zero)"
        else:
            check1["details"] = f"Substitution check: minimal_polynomial = {mp1} (expected z)"
    except Exception as e:
        check1["details"] = f"Error in substitution check: {str(e)}"
    checks.append(check1)
    
    # Check 2: Verify inequality simplification to (a+1)^2 < a^2 + 8
    check2 = {"name": "inequality_simplification", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": ""}
    try:
        a_sym = symbols('a', real=True, positive=True)
        x_sym = Rational(-1, 2) + a_sym**2 / 2
        
        # LHS: 4x^2 / (1 - sqrt(2x+1))^2 = 4x^2 / (1-a)^2
        lhs_num = 4 * x_sym**2
        lhs_denom = (1 - a_sym)**2
        lhs = lhs_num / lhs_denom
        
        # RHS: 2x + 9 = 2(-1/2 + a^2/2) + 9 = -1 + a^2 + 9 = a^2 + 8
        rhs = 2*x_sym + 9
        
        # Simplify LHS
        lhs_simplified = simplify(lhs)
        # Should equal (a^2 - 1)^2 / (1-a)^2 = (a-1)^2(a+1)^2 / (1-a)^2 = (a+1)^2
        expected_lhs = (a_sym + 1)**2
        diff_lhs = simplify(lhs_simplified - expected_lhs)
        
        rhs_simplified = simplify(rhs)
        expected_rhs = a_sym**2 + 8
        diff_rhs = simplify(rhs_simplified - expected_rhs)
        
        z = symbols('z')
        mp_lhs = minpoly(diff_lhs, z)
        mp_rhs = minpoly(diff_rhs, z)
        
        if mp_lhs == z and mp_rhs == z:
            check2["passed"] = True
            check2["details"] = f"Verified: LHS = (a+1)^2 and RHS = a^2 + 8"
        else:
            check2["details"] = f"LHS diff minimal_poly = {mp_lhs}, RHS diff minimal_poly = {mp_rhs}"
    except Exception as e:
        check2["details"] = f"Error in simplification: {str(e)}"
    checks.append(check2)
    
    # Check 3: Solve (a+1)^2 < a^2 + 8 to get a < 7/2
    check3 = {"name": "solve_for_a", "passed": False, "backend": "kdrag", "proof_type": "certificate", "details": ""}
    try:
        a = Real('a')
        # (a+1)^2 < a^2 + 8
        # a^2 + 2a + 1 < a^2 + 8
        # 2a + 1 < 8
        # 2a < 7
        # a < 7/2
        
        # Prove: a >= 0 AND (a+1)^2 < a^2 + 8 implies a < 7/2
        thm = kd.prove(
            ForAll([a], 
                Implies(
                    And(a >= 0, (a+1)**2 < a**2 + 8),
                    a < Rational(7, 2).as_numer_denom()[0] / Rational(7, 2).as_numer_denom()[1]
                )
            )
        )
        check3["passed"] = True
        check3["details"] = f"Z3 certificate: (a+1)^2 < a^2 + 8 AND a >= 0 implies a < 7/2"
    except Exception as e:
        check3["details"] = f"Z3 proof failed: {str(e)}\n{traceback.format_exc()}"
    checks.append(check3)
    
    # Check 4: Verify reverse: a < 7/2 implies inequality holds
    check4 = {"name": "reverse_implication", "passed": False, "backend": "kdrag", "proof_type": "certificate", "details": ""}
    try:
        a = Real('a')
        # Prove: 0 <= a < 7/2 implies (a+1)^2 < a^2 + 8
        thm = kd.prove(
            ForAll([a],
                Implies(
                    And(a >= 0, a < Rational(7, 2).as_numer_denom()[0] / Rational(7, 2).as_numer_denom()[1]),
                    (a+1)**2 < a**2 + 8
                )
            )
        )
        check4["passed"] = True
        check4["details"] = f"Z3 certificate: 0 <= a < 7/2 implies (a+1)^2 < a^2 + 8"
    except Exception as e:
        check4["details"] = f"Z3 proof failed: {str(e)}\n{traceback.format_exc()}"
    checks.append(check4)
    
    # Check 5: Convert a < 7/2 back to x bounds
    check5 = {"name": "convert_to_x_bounds", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": ""}
    try:
        # a < 7/2, a >= 0
        # x = -1/2 + a^2/2
        # When a = 0: x = -1/2
        # When a = 7/2: x = -1/2 + (7/2)^2/2 = -1/2 + 49/8 = 45/8
        
        x_min = Rational(-1, 2)
        a_max = Rational(7, 2)
        x_max_computed = Rational(-1, 2) + a_max**2 / 2
        x_max_expected = Rational(45, 8)
        
        diff = x_max_computed - x_max_expected
        if diff == 0:
            check5["passed"] = True
            check5["details"] = f"Verified: a=7/2 gives x=45/8, a=0 gives x=-1/2"
        else:
            check5["details"] = f"Mismatch: computed x_max={x_max_computed}, expected={x_max_expected}"
    except Exception as e:
        check5["details"] = f"Error: {str(e)}"
    checks.append(check5)
    
    # Check 6: Verify x=0 makes denominator zero (indeterminate)
    check6 = {"name": "x_zero_indeterminate", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": ""}
    try:
        # At x=0: 2x+1 = 1, sqrt(2x+1) = 1, denominator = (1-1)^2 = 0
        x_val = 0
        denom_at_zero = (1 - sym_sqrt(2*x_val + 1))**2
        if denom_at_zero == 0:
            check6["passed"] = True
            check6["details"] = f"Verified: at x=0, denominator = {denom_at_zero} (indeterminate)"
        else:
            check6["details"] = f"Denominator at x=0: {denom_at_zero} (expected 0)"
    except Exception as e:
        check6["details"] = f"Error: {str(e)}"
    checks.append(check6)
    
    # Check 7: Numerical verification at sample points
    check7 = {"name": "numerical_samples", "passed": False, "backend": "numerical", "proof_type": "numerical", "details": ""}
    try:
        import math
        test_points = [Rational(-1, 2), Rational(1, 1), Rational(2, 1), Rational(5, 1)]
        results = []
        all_pass = True
        
        for x_test in test_points:
            x_float = float(x_test)
            if x_float == 0:
                results.append(f"x={x_test}: skipped (indeterminate)")
                continue
            
            if 2*x_float + 1 < 0:
                results.append(f"x={x_test}: skipped (sqrt undefined)")
                continue
            
            lhs = 4*x_float**2 / (1 - math.sqrt(2*x_float + 1))**2
            rhs = 2*x_float + 9
            
            x_in_range = (x_test >= Rational(-1, 2) and x_test < Rational(45, 8) and x_test != 0)
            inequality_holds = lhs < rhs
            
            match = (x_in_range == inequality_holds)
            results.append(f"x={x_test}: LHS={lhs:.4f}, RHS={rhs:.4f}, holds={inequality_holds}, expected={x_in_range}, match={match}")
            if not match:
                all_pass = False
        
        check7["passed"] = all_pass
        check7["details"] = "; ".join(results)
    except Exception as e:
        check7["details"] = f"Error: {str(e)}"
    checks.append(check7)
    
    all_proved = all(c["passed"] for c in checks if c["proof_type"] in ["certificate", "symbolic_zero"])
    
    return {
        "proved": all_proved and checks[6]["passed"],
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        print(f"\n{check['name']}:")
        print(f"  Passed: {check['passed']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
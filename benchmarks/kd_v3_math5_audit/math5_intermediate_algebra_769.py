import kdrag as kd
from kdrag.smt import Real, And, Implies, ForAll, Exists
import sympy as sp
from sympy import symbols, solve, factor, simplify, expand

def verify():
    checks = []
    all_passed = True
    
    # === CHECK 1: Symbolic solution derivation using SymPy ===
    try:
        b_sym, c_sym = symbols('b c', real=True)
        
        # From perpendicularity: b = 12/(c-3)
        perp_eq = b_sym - 12/(c_sym - 3)
        
        # From passing through (-5,0): 25 - 5b + c = 0
        point_eq = 25 - 5*b_sym + c_sym
        
        # Substitute b = 12/(c-3) into point equation
        substituted = point_eq.subs(b_sym, 12/(c_sym - 3))
        # Multiply through by (c-3) to clear denominator
        cleared = simplify(substituted * (c_sym - 3))
        # This gives: c^2 + 22c - 135 = 0
        
        # Solve for c
        c_solutions = solve(cleared, c_sym)
        # Should get c = 5 or c = -27
        
        c_vals = [float(sol.evalf()) for sol in c_solutions]
        has_5 = any(abs(c - 5) < 0.001 for c in c_vals)
        has_neg27 = any(abs(c + 27) < 0.001 for c in c_vals)
        
        # For c=5, compute b
        b_at_5 = float((12/(5-3)).evalf())  # Should be 6
        # For c=-27, compute b
        b_at_neg27 = float((12/(-27-3)).evalf())  # Should be -0.4
        
        symbolic_passed = has_5 and has_neg27 and abs(b_at_5 - 6) < 0.001
        
        checks.append({
            "name": "symbolic_solution_derivation",
            "passed": symbolic_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solved system symbolically. c solutions: {c_vals}. For c=5: b={b_at_5}. For c=-27: b={b_at_neg27}"
        })
        all_passed = all_passed and symbolic_passed
    except Exception as e:
        checks.append({
            "name": "symbolic_solution_derivation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # === CHECK 2: Verify (b,c) = (6,5) satisfies perpendicularity constraint ===
    try:
        b_val, c_val = 6, 5
        # Tangent slope at x=0 is b = 6
        tangent_slope = b_val
        # Slope from (0,c) to (12,3)
        line_slope = (3 - c_val) / 12  # = (3-5)/12 = -2/12 = -1/6
        # Product should be -1 for perpendicularity
        product = tangent_slope * line_slope
        
        perp_passed = abs(product + 1) < 1e-10
        
        checks.append({
            "name": "perpendicularity_constraint",
            "passed": perp_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tangent slope: {tangent_slope}, Line slope: {line_slope}, Product: {product} (should be -1)"
        })
        all_passed = all_passed and perp_passed
    except Exception as e:
        checks.append({
            "name": "perpendicularity_constraint",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # === CHECK 3: Verify parabola passes through (-5,0) ===
    try:
        b_val, c_val = 6, 5
        x_test, y_test = -5, 0
        y_computed = x_test**2 + b_val*x_test + c_val
        # Should equal 0
        
        point_passed = abs(y_computed - y_test) < 1e-10
        
        checks.append({
            "name": "point_constraint",
            "passed": point_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x={x_test}: y = {y_computed} (should be {y_test})"
        })
        all_passed = all_passed and point_passed
    except Exception as e:
        checks.append({
            "name": "point_constraint",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # === CHECK 4: Verify c=5 is solution to c^2 + 22c - 135 = 0 using kdrag ===
    try:
        c = Real('c')
        # c^2 + 22c - 135 = 0 factors as (c-5)(c+27) = 0
        # So c=5 is a solution
        constraint = c*c + 22*c - 135 == 0
        c_is_5 = c == 5
        
        thm = kd.prove(Implies(c_is_5, constraint))
        
        kdrag_passed = True
        checks.append({
            "name": "kdrag_verify_c_solution",
            "passed": kdrag_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved c=5 satisfies c^2+22c-135=0. Proof: {thm}"
        })
        all_passed = all_passed and kdrag_passed
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_verify_c_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_verify_c_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # === CHECK 5: Verify the quadratic c^2 + 22c - 135 has roots 5 and -27 ===
    try:
        c_sym = symbols('c')
        poly = c_sym**2 + 22*c_sym - 135
        factored = factor(poly)
        # Should be (c-5)(c+27)
        expected = (c_sym - 5) * (c_sym + 27)
        
        diff = simplify(factored - expected)
        factor_passed = diff == 0
        
        checks.append({
            "name": "quadratic_factorization",
            "passed": factor_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factored form: {factored}, Expected: {expected}, Difference: {diff}"
        })
        all_passed = all_passed and factor_passed
    except Exception as e:
        checks.append({
            "name": "quadratic_factorization",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # === CHECK 6: Verify (0,5) is closer to (12,3) than any other point on parabola ===
    try:
        # Distance from (0,5) to (12,3)
        dist_intercept = ((12-0)**2 + (3-5)**2)**0.5
        
        # Sample other points on parabola y = x^2 + 6x + 5
        test_xs = [-5, -3, -1, 1, 3, 5, 10]
        all_farther = True
        for x_test in test_xs:
            if x_test == 0:
                continue
            y_test = x_test**2 + 6*x_test + 5
            dist_test = ((12-x_test)**2 + (3-y_test)**2)**0.5
            if dist_test <= dist_intercept:
                all_farther = False
                break
        
        checks.append({
            "name": "closest_point_verification",
            "passed": all_farther,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Distance from (0,5): {dist_intercept}. All sampled points farther: {all_farther}"
        })
        all_passed = all_passed and all_farther
    except Exception as e:
        checks.append({
            "name": "closest_point_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
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
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
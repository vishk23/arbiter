import kdrag as kd
from kdrag.smt import *
from sympy import symbols, sqrt, solve, simplify, expand, Poly, minimal_polynomial, Rational
from sympy import N as sympy_N

def verify():
    checks = []
    all_passed = True
    
    # ====================================================================
    # CHECK 1: Verify substitution y = x^2 + 18x + 30 transforms correctly
    # ====================================================================
    try:
        x_sym = symbols('x', real=True)
        y_sym = symbols('y', real=True)
        
        # Original equation: x^2 + 18x + 30 = 2*sqrt(x^2 + 18x + 45)
        # With y = x^2 + 18x + 30, we have:
        # y = 2*sqrt(y + 15)
        
        # Verify algebraically that if y = x^2 + 18x + 30, then
        # x^2 + 18x + 45 = y + 15
        lhs = x_sym**2 + 18*x_sym + 45
        rhs = (x_sym**2 + 18*x_sym + 30) + 15
        diff = simplify(lhs - rhs)
        
        check1_passed = (diff == 0)
        checks.append({
            "name": "substitution_validity",
            "passed": check1_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified y = x^2+18x+30 transforms x^2+18x+45 to y+15. Difference: {diff}"
        })
        all_passed = all_passed and check1_passed
    except Exception as e:
        checks.append({
            "name": "substitution_validity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # ====================================================================
    # CHECK 2: Solve y = 2*sqrt(y+15) and verify y=10 is the only valid solution
    # ====================================================================
    try:
        # Squaring both sides: y^2 = 4(y+15) => y^2 - 4y - 60 = 0
        y_solutions = solve(y_sym**2 - 4*y_sym - 60, y_sym)
        
        # Check which solutions satisfy the original equation y = 2*sqrt(y+15)
        valid_y = []
        for y_val in y_solutions:
            if y_val + 15 >= 0:  # sqrt argument must be non-negative
                lhs_val = y_val
                rhs_val = 2*sqrt(y_val + 15)
                if simplify(lhs_val - rhs_val) == 0:
                    valid_y.append(y_val)
        
        check2_passed = (len(valid_y) == 1 and valid_y[0] == 10)
        checks.append({
            "name": "y_equation_solution",
            "passed": check2_passed,
            "backend": "sympy",
            "proof_type": "equation_solving",
            "details": f"Solutions to y^2-4y-60=0: {y_solutions}, Valid (y=2*sqrt(y+15)): {valid_y}"
        })
        all_passed = all_passed and check2_passed
    except Exception as e:
        checks.append({
            "name": "y_equation_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "equation_solving",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # ====================================================================
    # CHECK 3: Solve x^2 + 18x + 30 = 10 for real roots
    # ====================================================================
    try:
        # x^2 + 18x + 30 = 10 => x^2 + 18x + 20 = 0
        x_solutions = solve(x_sym**2 + 18*x_sym + 20, x_sym)
        
        # Verify these are real
        real_x_solutions = [sol for sol in x_solutions if sol.is_real]
        
        check3_passed = (len(real_x_solutions) == 2)
        checks.append({
            "name": "x_solutions_real",
            "passed": check3_passed,
            "backend": "sympy",
            "proof_type": "equation_solving",
            "details": f"Solutions to x^2+18x+20=0: {x_solutions}, Real solutions: {real_x_solutions}"
        })
        all_passed = all_passed and check3_passed
    except Exception as e:
        checks.append({
            "name": "x_solutions_real",
            "passed": False,
            "backend": "sympy",
            "proof_type": "equation_solving",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # ====================================================================
    # CHECK 4: Verify product of roots is 20
    # ====================================================================
    try:
        # For x^2 + 18x + 20 = 0, by Vieta's formulas, product of roots = c/a = 20/1 = 20
        poly = Poly(x_sym**2 + 18*x_sym + 20, x_sym)
        coeffs = poly.all_coeffs()
        product_vieta = coeffs[2] / coeffs[0]  # c/a
        
        # Also compute directly
        if len(real_x_solutions) == 2:
            product_direct = simplify(real_x_solutions[0] * real_x_solutions[1])
        else:
            product_direct = None
        
        check4_passed = (product_vieta == 20 and (product_direct is None or product_direct == 20))
        checks.append({
            "name": "product_of_roots",
            "passed": check4_passed,
            "backend": "sympy",
            "proof_type": "vieta_formula",
            "details": f"Product by Vieta: {product_vieta}, Product direct: {product_direct}"
        })
        all_passed = all_passed and check4_passed
    except Exception as e:
        checks.append({
            "name": "product_of_roots",
            "passed": False,
            "backend": "sympy",
            "proof_type": "vieta_formula",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # ====================================================================
    # CHECK 5: Verify the roots satisfy the original equation
    # ====================================================================
    try:
        verification_results = []
        for root in real_x_solutions:
            lhs = root**2 + 18*root + 30
            rhs = 2*sqrt(root**2 + 18*root + 45)
            diff = simplify(lhs - rhs)
            verification_results.append(diff == 0)
        
        check5_passed = all(verification_results)
        checks.append({
            "name": "roots_satisfy_original",
            "passed": check5_passed,
            "backend": "sympy",
            "proof_type": "equation_verification",
            "details": f"Verification for each root: {verification_results}"
        })
        all_passed = all_passed and check5_passed
    except Exception as e:
        checks.append({
            "name": "roots_satisfy_original",
            "passed": False,
            "backend": "sympy",
            "proof_type": "equation_verification",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    return all_passed, checks
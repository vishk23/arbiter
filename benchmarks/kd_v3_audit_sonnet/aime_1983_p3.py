import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And, Or, Not, Sqrt
import sympy as sp
from sympy import Symbol, sqrt, expand, solve, Poly, minimal_polynomial, Q

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify substitution y = x^2 + 18x + 30 leads to y = 2*sqrt(y+15)
    check1 = {
        "name": "substitution_correctness",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x_sym = Symbol('x', real=True)
        y_sym = Symbol('y', real=True)
        original_eq = x_sym**2 + 18*x_sym + 30 - 2*sqrt(x_sym**2 + 18*x_sym + 45)
        substituted = original_eq.subs(x_sym**2 + 18*x_sym + 30, y_sym)
        target = y_sym - 2*sqrt(y_sym + 15)
        difference = sp.simplify(substituted - target)
        check1["passed"] = (difference == 0)
        check1["details"] = f"Substitution y=x^2+18x+30 transforms equation correctly: diff={difference}"
        all_passed &= check1["passed"]
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Solve y = 2*sqrt(y+15) to get y=10 (reject y=-6 as extraneous)
    check2 = {
        "name": "solve_y_equation",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        y = Symbol('y', real=True)
        eq = y - 2*sqrt(y + 15)
        squared = eq**2
        expanded = sp.expand(squared)
        poly = Poly(expanded, y)
        solutions = solve(y**2 - 4*(y+15), y)
        check2["passed"] = (10 in solutions and -6 in solutions)
        y_val = 10
        lhs = y_val
        rhs = 2*sqrt(y_val + 15)
        verification = sp.simplify(lhs - rhs)
        check2["passed"] &= (verification == 0)
        y_val_bad = -6
        lhs_bad = y_val_bad
        rhs_bad = 2*sqrt(y_val_bad + 15)
        check2["passed"] &= (lhs_bad != rhs_bad)
        check2["details"] = f"Solutions: {solutions}, y=10 valid: {verification==0}, y=-6 invalid (extraneous)"
        all_passed &= check2["passed"]
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Substitute back y=10 to get x^2+18x+20=0
    check3 = {
        "name": "back_substitution",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x = Symbol('x', real=True)
        eq_after_sub = x**2 + 18*x + 30 - 10
        simplified = sp.simplify(eq_after_sub)
        target = x**2 + 18*x + 20
        check3["passed"] = (simplified == target)
        check3["details"] = f"After y=10 substitution: {simplified} == {target}"
        all_passed &= check3["passed"]
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Verify discriminant is positive (both roots real)
    check4 = {
        "name": "discriminant_positive",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        a, b, c = 1, 18, 20
        discriminant = b**2 - 4*a*c
        check4["passed"] = (discriminant == 244 and discriminant > 0)
        check4["details"] = f"Discriminant = {discriminant} > 0, both roots are real"
        all_passed &= check4["passed"]
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Vieta's formula - product of roots is c/a = 20
    check5 = {
        "name": "vieta_product",
        "backend": "sympy",
        "proof_type": "certificate"
    }
    try:
        x = Symbol('x', real=True)
        poly = x**2 + 18*x + 20
        roots = solve(poly, x)
        product = sp.simplify(roots[0] * roots[1])
        vieta_product = 20
        check5["passed"] = (product == vieta_product == 20)
        check5["details"] = f"Product of roots via Vieta: c/a = 20/1 = 20, computed: {product}"
        all_passed &= check5["passed"]
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check5)
    
    # Check 6: Rigorous algebraic verification using minimal polynomial
    check6 = {
        "name": "algebraic_certificate",
        "backend": "sympy",
        "proof_type": "certificate"
    }
    try:
        x = Symbol('x', real=True)
        poly = x**2 + 18*x + 20
        roots = solve(poly, x)
        product = roots[0] * roots[1]
        t = Symbol('t')
        mp = minimal_polynomial(product - 20, t)
        check6["passed"] = (mp == t)
        check6["details"] = f"minimal_polynomial(product - 20) = {mp}, proves product = 20 exactly"
        all_passed &= check6["passed"]
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check6)
    
    # Check 7: Numerical verification - plug in actual roots
    check7 = {
        "name": "numerical_verification",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        x = Symbol('x', real=True)
        final_poly = x**2 + 18*x + 20
        roots = solve(final_poly, x)
        root1_val = complex(roots[0].evalf())
        root2_val = complex(roots[1].evalf())
        original_lhs1 = root1_val**2 + 18*root1_val + 30
        original_rhs1 = 2*sp.sqrt(root1_val**2 + 18*root1_val + 45)
        original_lhs2 = root2_val**2 + 18*root2_val + 30
        original_rhs2 = 2*sp.sqrt(root2_val**2 + 18*root2_val + 45)
        diff1 = abs(complex(original_lhs1) - complex(original_rhs1))
        diff2 = abs(complex(original_lhs2) - complex(original_rhs2))
        product_numerical = root1_val * root2_val
        check7["passed"] = (diff1 < 1e-10 and diff2 < 1e-10 and abs(product_numerical - 20) < 1e-10)
        check7["details"] = f"Roots satisfy original equation (errors: {diff1:.2e}, {diff2:.2e}), product≈{product_numerical.real:.6f}"
        all_passed &= check7["passed"]
    except Exception as e:
        check7["passed"] = False
        check7["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check7)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details']}")
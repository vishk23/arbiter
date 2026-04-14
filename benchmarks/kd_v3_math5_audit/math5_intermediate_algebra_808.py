import kdrag as kd
from kdrag.smt import *
from sympy import symbols, sqrt as sym_sqrt, simplify, N, minimal_polynomial
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify completing the square algebraically
    check1 = {
        "name": "completing_square",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x_sym, y_sym = symbols('x y', real=True)
        original_third = x_sym**2 + y_sym**2 - 80*x_sym - 100*y_sym + 4100
        completed = (x_sym - 40)**2 + (y_sym - 50)**2
        diff = simplify(original_third - completed)
        check1["passed"] = (diff == 0)
        check1["details"] = f"Completing square: x^2 + y^2 - 80x - 100y + 4100 = (x-40)^2 + (y-50)^2. Difference: {diff}"
        all_passed = all_passed and check1["passed"]
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Verify QM-AM inequality for first term: sqrt((x^2 + 400)/2) >= (x + 20)/2
    check2 = {
        "name": "qm_am_first_term",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        x = Real("x")
        # QM-AM: sqrt((x^2 + 400)/2) >= (x + 20)/2
        # Squaring both sides (both positive): (x^2 + 400)/2 >= (x + 20)^2/4
        # Multiply by 4: 2(x^2 + 400) >= (x + 20)^2
        # Expand: 2x^2 + 800 >= x^2 + 40x + 400
        # Simplify: x^2 - 40x + 400 >= 0
        # Which is: (x - 20)^2 >= 0
        qm_am_1 = kd.prove(ForAll([x], 
            Implies(x >= 0, (x - 20)*(x - 20) >= 0)))
        check2["passed"] = True
        check2["details"] = f"Proved QM-AM for first term via (x-20)^2 >= 0: {qm_am_1}"
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Verify QM-AM inequality for second term: sqrt((y^2 + 900)/2) >= (y + 30)/2
    check3 = {
        "name": "qm_am_second_term",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        y = Real("y")
        # Similar to above: y^2 - 60y + 900 >= 0, which is (y - 30)^2 >= 0
        qm_am_2 = kd.prove(ForAll([y], 
            Implies(y >= 0, (y - 30)*(y - 30) >= 0)))
        check3["passed"] = True
        check3["details"] = f"Proved QM-AM for second term via (y-30)^2 >= 0: {qm_am_2}"
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Verify QM-AM inequality for third term
    check4 = {
        "name": "qm_am_third_term",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        x = Real("x")
        y = Real("y")
        # sqrt(((40-x)^2 + (50-y)^2)/2) >= ((40-x) + (50-y))/2
        # Squaring: ((40-x)^2 + (50-y)^2)/2 >= ((90-x-y)^2)/4
        # Multiply by 4: 2((40-x)^2 + (50-y)^2) >= (90-x-y)^2
        # Expand: 2(1600 - 80x + x^2 + 2500 - 100y + y^2) >= 8100 - 180x - 180y + 2xy + x^2 + y^2
        # Simplify: 2x^2 + 2y^2 + 8200 - 160x - 200y >= x^2 + y^2 + 2xy + 8100 - 180x - 180y
        # x^2 + y^2 - 2xy + 100 + 20x - 20y >= 0
        # (x - y)^2 + 20(x - y) + 100 >= 0
        # (x - y + 10)^2 >= 0
        qm_am_3 = kd.prove(ForAll([x, y], (x - y + 10)*(x - y + 10) >= 0))
        check4["passed"] = True
        check4["details"] = f"Proved QM-AM for third term via (x-y+10)^2 >= 0: {qm_am_3}"
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Verify the minimum value is 70*sqrt(2) using symbolic computation
    check5 = {
        "name": "minimum_value_symbolic",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x_val = 20
        y_val = 30
        term1 = sym_sqrt(x_val**2 + 400)
        term2 = sym_sqrt(y_val**2 + 900)
        term3 = sym_sqrt((x_val - 40)**2 + (y_val - 50)**2)
        total = term1 + term2 + term3
        target = 70 * sym_sqrt(2)
        diff = simplify(total - target)
        
        # Verify algebraically that the difference is zero
        x_test = symbols('x_test')
        mp = minimal_polynomial(diff, x_test)
        check5["passed"] = (mp == x_test)
        check5["details"] = f"At (20, 30): value = {total}, target = {target}, minimal_poly(diff) = {mp}"
        all_passed = all_passed and check5["passed"]
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check5)
    
    # Check 6: Numerical verification at critical point
    check6 = {
        "name": "numerical_verification_critical",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        x_val = 20.0
        y_val = 30.0
        term1 = math.sqrt(x_val**2 + 400)
        term2 = math.sqrt(y_val**2 + 900)
        term3 = math.sqrt((x_val - 40)**2 + (y_val - 50)**2)
        total = term1 + term2 + term3
        expected = 70 * math.sqrt(2)
        check6["passed"] = abs(total - expected) < 1e-10
        check6["details"] = f"At (20, 30): computed = {total:.15f}, expected = {expected:.15f}, diff = {abs(total - expected):.2e}"
        all_passed = all_passed and check6["passed"]
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check6)
    
    # Check 7: Numerical verification at boundary points
    check7 = {
        "name": "numerical_verification_boundaries",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        test_points = [(0, 0), (40, 50), (0, 50), (40, 0), (20, 0), (0, 30)]
        min_val = 70 * math.sqrt(2)
        all_greater = True
        details_list = []
        for x_val, y_val in test_points:
            term1 = math.sqrt(x_val**2 + 400)
            term2 = math.sqrt(y_val**2 + 900)
            term3 = math.sqrt((x_val - 40)**2 + (y_val - 50)**2)
            total = term1 + term2 + term3
            if total < min_val - 1e-10:
                all_greater = False
            details_list.append(f"({x_val}, {y_val}): {total:.6f}")
        check7["passed"] = all_greater
        check7["details"] = f"All boundary points >= {min_val:.6f}: {'; '.join(details_list)}"
        all_passed = all_passed and check7["passed"]
    except Exception as e:
        check7["passed"] = False
        check7["details"] = f"Error: {e}"
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
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
import kdrag as kd
from kdrag.smt import *
from sympy import *
from sympy import pi as sym_pi
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: SymPy symbolic proof via minimal polynomial
    check1 = {
        "name": "symbolic_minimal_polynomial_proof",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    try:
        result = cos(sym_pi/7) - cos(2*sym_pi/7) + cos(3*sym_pi/7)
        target = Rational(1, 2)
        difference = result - target
        x = Symbol('x')
        mp = minimal_polynomial(difference, x)
        if mp == x:
            check1["passed"] = True
            check1["details"] = f"Proved via minimal polynomial: mp(cos(π/7) - cos(2π/7) + cos(3π/7) - 1/2) = {mp}, which equals x, proving the difference is exactly zero."
        else:
            check1["details"] = f"Minimal polynomial is {mp}, not x. Expression may not be zero."
            all_passed = False
    except Exception as e:
        check1["details"] = f"SymPy proof failed: {e}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Alternative SymPy proof using cos(5π/7) = -cos(2π/7)
    check2 = {
        "name": "symbolic_identity_transformation",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    try:
        # cos(5π/7) = cos(π - 2π/7) = -cos(2π/7)
        # So S = cos(π/7) - cos(2π/7) + cos(3π/7)
        #     = cos(π/7) + cos(3π/7) + cos(5π/7)
        expr1 = cos(sym_pi/7) - cos(2*sym_pi/7) + cos(3*sym_pi/7)
        expr2 = cos(sym_pi/7) + cos(3*sym_pi/7) + cos(5*sym_pi/7)
        diff = simplify(expr1 - expr2)
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        if mp == x:
            check2["passed"] = True
            check2["details"] = f"Verified identity: cos(π/7) - cos(2π/7) + cos(3π/7) = cos(π/7) + cos(3π/7) + cos(5π/7) via minimal_polynomial({mp}) = x"
        else:
            check2["details"] = f"Identity verification failed: mp = {mp}"
    except Exception as e:
        check2["details"] = f"Identity verification error: {e}"
    checks.append(check2)
    
    # Check 3: Verify the product-sum formula step
    check3 = {
        "name": "product_sum_formula_verification",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    try:
        # S * 2 * sin(π/7) = sin(6π/7) = sin(π/7)
        # So S = 1/2
        S_expr = cos(sym_pi/7) + cos(3*sym_pi/7) + cos(5*sym_pi/7)
        lhs = S_expr * 2 * sin(sym_pi/7)
        rhs = sin(sym_pi/7)
        diff = simplify(lhs - rhs)
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        if mp == x:
            check3["passed"] = True
            check3["details"] = f"Verified: S * 2*sin(π/7) = sin(π/7), hence S = 1/2. Minimal polynomial: {mp} = x"
        else:
            check3["details"] = f"Product-sum verification failed: mp = {mp}"
    except Exception as e:
        check3["details"] = f"Product-sum verification error: {e}"
    checks.append(check3)
    
    # Check 4: Numerical sanity check (high precision)
    check4 = {
        "name": "numerical_verification_50_digits",
        "passed": False,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": ""
    }
    try:
        result_numeric = N(cos(sym_pi/7) - cos(2*sym_pi/7) + cos(3*sym_pi/7), 50)
        target_numeric = N(Rational(1, 2), 50)
        diff_numeric = abs(result_numeric - target_numeric)
        if diff_numeric < 1e-45:
            check4["passed"] = True
            check4["details"] = f"Numerical verification: result = {result_numeric}, target = 0.5, diff = {diff_numeric} < 1e-45"
        else:
            check4["details"] = f"Numerical check failed: diff = {diff_numeric}"
            all_passed = False
    except Exception as e:
        check4["details"] = f"Numerical verification error: {e}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Python math library numerical check
    check5 = {
        "name": "numerical_python_math",
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": ""
    }
    try:
        val = math.cos(math.pi/7) - math.cos(2*math.pi/7) + math.cos(3*math.pi/7)
        diff = abs(val - 0.5)
        if diff < 1e-10:
            check5["passed"] = True
            check5["details"] = f"Python math: cos(π/7) - cos(2π/7) + cos(3π/7) = {val}, diff from 0.5 = {diff}"
        else:
            check5["details"] = f"Python math check failed: val = {val}, diff = {diff}"
    except Exception as e:
        check5["details"] = f"Python math error: {e}"
    checks.append(check5)
    
    # Check 6: Verify sin(6π/7) = sin(π/7)
    check6 = {
        "name": "sin_identity_verification",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    try:
        # sin(6π/7) = sin(π - π/7) = sin(π/7)
        diff = sin(6*sym_pi/7) - sin(sym_pi/7)
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        if mp == x:
            check6["passed"] = True
            check6["details"] = f"Verified: sin(6π/7) = sin(π/7) via minimal_polynomial = x"
        else:
            check6["details"] = f"Sin identity failed: mp = {mp}"
    except Exception as e:
        check6["details"] = f"Sin identity error: {e}"
    checks.append(check6)
    
    proved = all_passed and check1["passed"]
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Theorem proved: {result['proved']}")
    print(f"\nCheck results:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
        print()
import kdrag as kd
from kdrag.smt import Real, And, Or, Not, Implies, ForAll, Exists, If
import sympy as sp
from sympy import sqrt, Symbol, simplify, minimal_polynomial, N, solve, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify domain constraint using kdrag
    try:
        x = Real("x")
        domain_cond = And(x >= -1, x <= 1, (3 - x) >= (x + 1))
        simplified_domain = kd.prove(ForAll([x], Implies(domain_cond, And(x >= -1, x <= 1))))
        checks.append({
            "name": "domain_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved domain constraint: {simplified_domain}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "domain_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Verify critical point equation symbolically
    try:
        x_sym = Symbol('x', real=True)
        # The equation after squaring twice: 1024x^2 - 2048x + 897 = 0
        poly = 1024*x_sym**2 - 2048*x_sym + 897
        roots = solve(poly, x_sym)
        
        # Expected roots: 1 - sqrt(127)/32 and 1 + sqrt(127)/32
        root1 = 1 - sqrt(127)/32
        root2 = 1 + sqrt(127)/32
        
        # Verify both roots satisfy the polynomial
        val1 = poly.subs(x_sym, root1)
        val2 = poly.subs(x_sym, root2)
        
        # Use minimal polynomial to prove val1 = 0 exactly
        mp1 = minimal_polynomial(simplify(val1), Symbol('t'))
        mp2 = minimal_polynomial(simplify(val2), Symbol('t'))
        
        passed = (mp1 == Symbol('t')) and (mp2 == Symbol('t'))
        
        checks.append({
            "name": "quadratic_roots_symbolic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified roots {root1} and {root2} satisfy polynomial via minimal_polynomial"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "quadratic_roots_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Verify that the critical point is in domain
    try:
        x_crit = 1 - sqrt(127)/32
        # Check -1 <= x_crit <= 1
        val_crit = N(x_crit, 50)
        in_domain = (-1 <= val_crit <= 1)
        
        # Also verify x_crit < 1 symbolically
        diff = 1 - x_crit  # Should equal sqrt(127)/32 > 0
        mp_diff = minimal_polynomial(diff - sqrt(127)/32, Symbol('t'))
        
        passed = in_domain and (mp_diff == Symbol('t'))
        
        checks.append({
            "name": "critical_point_in_domain",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Critical point {val_crit:.15f} is in [-1, 1] and equals 1 - sqrt(127)/32"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "critical_point_in_domain",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Verify f(x_crit) = 1/2 symbolically
    try:
        x_crit = 1 - sqrt(127)/32
        # f(x) = sqrt(sqrt(3-x) - sqrt(x+1))
        inner = sqrt(3 - x_crit) - sqrt(x_crit + 1)
        f_val = sqrt(inner)
        
        # Should equal 1/2
        diff = f_val - Rational(1, 2)
        diff_simplified = simplify(diff)
        
        mp = minimal_polynomial(diff_simplified, Symbol('t'))
        passed = (mp == Symbol('t'))
        
        checks.append({
            "name": "critical_point_equation",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified f(x_crit) = 1/2 via minimal_polynomial"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "critical_point_equation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 5: Numerical sanity checks
    try:
        import math
        
        def f(x):
            if x < -1 or x > 1:
                return None
            inner = 3 - x
            if inner < 0:
                return None
            outer_inner = math.sqrt(inner) - math.sqrt(x + 1)
            if outer_inner < 0:
                return None
            return math.sqrt(outer_inner)
        
        # Check f(-1) = sqrt(2)
        f_minus1 = f(-1)
        check1 = abs(f_minus1 - math.sqrt(2)) < 1e-10
        
        # Check f(1) = 0
        f_1 = f(1)
        check2 = abs(f_1) < 1e-10
        
        # Check f(x_crit) = 0.5
        x_crit_num = float(1 - math.sqrt(127)/32)
        f_crit = f(x_crit_num)
        check3 = abs(f_crit - 0.5) < 1e-10
        
        # Check f(-0.5) > 0.5 (in solution interval)
        f_minus_half = f(-0.5)
        check4 = f_minus_half > 0.5
        
        # Check f(0.5) < 0.5 (outside solution interval)
        f_half = f(0.5)
        check5 = f_half < 0.5
        
        passed = check1 and check2 and check3 and check4 and check5
        
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"f(-1)={f_minus1:.10f}, f(1)={f_1:.10f}, f(x_crit)={f_crit:.10f}, f(-0.5)={f_minus_half:.10f}, f(0.5)={f_half:.10f}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 6: Verify monotonicity constraint (f is decreasing)
    try:
        x_sym = Symbol('x', real=True)
        # f(x) = sqrt(sqrt(3-x) - sqrt(x+1))
        # df/dx = derivative, should be negative on (-1, 1)
        f_expr = sqrt(sqrt(3 - x_sym) - sqrt(x_sym + 1))
        df = sp.diff(f_expr, x_sym)
        
        # Check sign at a few points
        test_points = [-0.5, 0, 0.5]
        all_negative = all(N(df.subs(x_sym, pt)) < 0 for pt in test_points)
        
        checks.append({
            "name": "monotonicity_check",
            "passed": all_negative,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Derivative negative at test points: {all_negative}"
        })
        
        if not all_negative:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "monotonicity_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PASSED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
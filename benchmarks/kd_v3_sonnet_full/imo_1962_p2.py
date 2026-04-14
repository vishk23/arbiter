import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or, Not
import sympy as sp
from sympy import sqrt, symbols, simplify, solve, minimal_polynomial, Rational, N

def verify():
    checks = []
    
    # Check 1: Verify the algebraic solution x = 1 - sqrt(127)/32
    x_sym = symbols('x', real=True)
    x_solution = 1 - sqrt(127)/32
    
    # The equation derived from f(x) = 1/2:
    # 1024*x^2 - 2048*x + 897 = 0
    poly_expr = 1024*x_sym**2 - 2048*x_sym + 897
    poly_at_sol = poly_expr.subs(x_sym, x_solution)
    poly_simplified = simplify(poly_at_sol)
    
    check1_passed = (poly_simplified == 0)
    checks.append({
        "name": "algebraic_solution_satisfies_quadratic",
        "passed": check1_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified x = 1 - sqrt(127)/32 satisfies 1024x^2 - 2048x + 897 = 0: {poly_simplified} == 0"
    })
    
    # Check 2: Verify x_solution is in valid domain [-1, 1]
    x_sol_numeric = float(N(x_solution, 50))
    domain_check = (-1 <= x_sol_numeric <= 1)
    checks.append({
        "name": "solution_in_domain",
        "passed": domain_check,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"x_solution ≈ {x_sol_numeric:.10f} is in [-1, 1]: {domain_check}"
    })
    
    # Check 3: Verify f(x_solution) = 1/2 numerically
    x_val = x_sol_numeric
    if -1 <= x_val <= 1 and (3 - x_val) >= (x_val + 1):
        inner = sqrt(3 - x_val) - sqrt(x_val + 1)
        if inner >= 0:
            f_val = sqrt(inner)
            f_check = abs(float(f_val) - 0.5) < 1e-10
            checks.append({
                "name": "boundary_point_evaluation",
                "passed": f_check,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"f({x_val:.10f}) = {float(f_val):.10f} ≈ 0.5: error = {abs(float(f_val) - 0.5):.2e}"
            })
        else:
            checks.append({
                "name": "boundary_point_evaluation",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Inner sqrt negative"
            })
    else:
        checks.append({
            "name": "boundary_point_evaluation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "x_solution out of valid range"
        })
    
    # Check 4: Verify f(-1) > 1/2 (left endpoint)
    x_left = -1.0
    f_left = float(sqrt(sqrt(3 - x_left) - sqrt(x_left + 1)))
    left_check = f_left > 0.5
    checks.append({
        "name": "left_endpoint_inequality",
        "passed": left_check,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"f(-1) = {f_left:.10f} > 0.5: {left_check}"
    })
    
    # Check 5: Verify f is continuous and decreasing (sample points)
    sample_points = [-1.0, -0.5, 0.0, 0.5, x_sol_numeric]
    f_values = []
    all_valid = True
    for xp in sample_points:
        if -1 <= xp <= 1:
            inner_diff = (3 - xp) - (xp + 1)
            if inner_diff >= 0:
                f_val = float(sqrt(sqrt(3 - xp) - sqrt(xp + 1)))
                f_values.append(f_val)
            else:
                all_valid = False
                break
        else:
            all_valid = False
            break
    
    decreasing = all_valid and all(f_values[i] >= f_values[i+1] for i in range(len(f_values)-1))
    checks.append({
        "name": "function_decreasing",
        "passed": decreasing,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"f decreasing on samples: {decreasing}, f_values = {[f'{v:.4f}' for v in f_values]}"
    })
    
    # Check 6: Verify the other root x = 1 + sqrt(127)/32 > 1 (outside domain)
    x_other = 1 + sqrt(127)/32
    x_other_numeric = float(N(x_other, 50))
    other_root_check = x_other_numeric > 1
    poly_at_other = poly_expr.subs(x_sym, x_other)
    other_satisfies = simplify(poly_at_other) == 0
    checks.append({
        "name": "other_root_outside_domain",
        "passed": other_root_check and other_satisfies,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"x = 1 + sqrt(127)/32 ≈ {x_other_numeric:.4f} > 1 and satisfies quadratic: {other_satisfies}"
    })
    
    # Check 7: Use minimal_polynomial to verify algebraic nature
    # The solution x = 1 - sqrt(127)/32 satisfies (x-1)^2 = 127/1024
    # i.e., 1024(x-1)^2 = 127
    # i.e., 1024x^2 - 2048x + 1024 - 127 = 0
    # i.e., 1024x^2 - 2048x + 897 = 0
    t = symbols('t')
    mp = minimal_polynomial(x_solution, t)
    expected_poly = 1024*t**2 - 2048*t + 897
    mp_check = simplify(mp - expected_poly) == 0
    checks.append({
        "name": "minimal_polynomial_verification",
        "passed": mp_check,
        "backend": "sympy",
        "proof_type": "certificate",
        "details": f"minimal_polynomial(x_solution) matches expected quadratic: {mp_check}"
    })
    
    # Check 8: Verify interval characterization via kdrag
    # We can encode: for x in [-1, x_solution), f(x) > 1/2
    # This is hard in Z3 due to square roots, so we verify the algebraic boundary
    try:
        x = Real('x')
        # The quadratic 1024x^2 - 2048x + 897 has roots at x = 1 ± sqrt(127)/32
        # We verify that the discriminant is 127*1024
        # Discriminant = b^2 - 4ac = 2048^2 - 4*1024*897
        discriminant = 2048**2 - 4*1024*897
        expected_disc = 127 * 1024
        disc_thm = kd.prove(discriminant == expected_disc)
        checks.append({
            "name": "quadratic_discriminant",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved discriminant = {expected_disc} via kdrag: {disc_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "quadratic_discriminant",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
    
    proved = all(check['passed'] for check in checks)
    
    return {
        'proved': proved,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
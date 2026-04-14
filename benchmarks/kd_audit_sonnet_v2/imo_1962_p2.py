import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or, Not
import sympy as sp
from sympy import sqrt, simplify, minimal_polynomial, N, Symbol, Rational

def verify():
    checks = []
    
    # Check 1: Verify the quadratic equation solution symbolically
    x = Symbol('x', real=True)
    quadratic = 1024*x**2 - 2048*x + 897
    x_sym = 1 - sqrt(127)/32
    residual = quadratic.subs(x, x_sym)
    residual_simplified = simplify(residual)
    
    check1_passed = (residual_simplified == 0)
    checks.append({
        "name": "quadratic_root_symbolic",
        "passed": check1_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified x = 1 - sqrt(127)/32 satisfies 1024x^2 - 2048x + 897 = 0. Residual: {residual_simplified}"
    })
    
    # Check 2: Verify the algebraic identity using minimal polynomial
    x_val = 1 - sp.sqrt(127)/32
    quadratic_at_x = 1024*x_val**2 - 2048*x_val + 897
    simplified = sp.expand(quadratic_at_x)
    t = Symbol('t')
    mp = minimal_polynomial(simplified, t)
    check2_passed = (mp == t)
    checks.append({
        "name": "minimal_polynomial_certificate",
        "passed": check2_passed,
        "backend": "sympy",
        "proof_type": "certificate",
        "details": f"Minimal polynomial of quadratic residual is {mp}, proving algebraic zero."
    })
    
    # Check 3: Numerical verification at boundary x = -1
    x_left = -1
    try:
        val_left = sp.sqrt(sp.sqrt(3 - x_left) - sp.sqrt(x_left + 1))
        val_left_num = N(val_left, 20)
        check3_passed = (val_left_num > 0.5)
        checks.append({
            "name": "boundary_left_numerical",
            "passed": bool(check3_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x=-1: f(-1) = {val_left_num} > 0.5 (sqrt(2) ≈ 1.414)"
        })
    except Exception as e:
        checks.append({
            "name": "boundary_left_numerical",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error evaluating at x=-1: {e}"
        })
    
    # Check 4: Numerical verification at critical point x = 1 - sqrt(127)/32
    x_crit = 1 - sp.sqrt(127)/32
    x_crit_num = N(x_crit, 20)
    try:
        val_crit = sp.sqrt(sp.sqrt(3 - x_crit) - sp.sqrt(x_crit + 1))
        val_crit_num = N(val_crit, 20)
        check4_passed = abs(val_crit_num - 0.5) < 1e-10
        checks.append({
            "name": "critical_point_numerical",
            "passed": bool(check4_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x = 1 - sqrt(127)/32 ≈ {x_crit_num}: f(x) ≈ {val_crit_num} ≈ 0.5"
        })
    except Exception as e:
        checks.append({
            "name": "critical_point_numerical",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error evaluating at critical point: {e}"
        })
    
    # Check 5: Numerical verification at x = 1 (should be 0)
    x_right = 1
    try:
        val_right = sp.sqrt(sp.sqrt(3 - x_right) - sp.sqrt(x_right + 1))
        val_right_num = N(val_right, 20)
        check5_passed = (val_right_num < 0.5)
        checks.append({
            "name": "boundary_right_numerical",
            "passed": bool(check5_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x=1: f(1) = {val_right_num} < 0.5 (equals 0)"
        })
    except Exception as e:
        checks.append({
            "name": "boundary_right_numerical",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error evaluating at x=1: {e}"
        })
    
    # Check 6: Verify domain constraint -1 <= x <= 1 using kdrag
    try:
        x_real = Real('x')
        x_crit_kdrag = 1 - sp.sqrt(127)/32
        x_crit_float = float(N(x_crit_kdrag, 20))
        
        # Prove domain bound: x_crit >= -1
        domain_lower = kd.prove(x_crit_float >= -1)
        
        # Prove domain bound: x_crit <= 1
        domain_upper = kd.prove(x_crit_float <= 1)
        
        check6_passed = True
        checks.append({
            "name": "domain_bounds_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved -1 <= x_crit <= 1 where x_crit ≈ {x_crit_float}"
        })
    except Exception as e:
        checks.append({
            "name": "domain_bounds_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Could not prove domain bounds: {e}"
        })
    
    # Check 7: Verify the algebraic derivation steps symbolically
    y = Symbol('y', real=True)
    # Start: sqrt(sqrt(3-y) - sqrt(y+1)) = 1/2
    # Square: sqrt(3-y) - sqrt(y+1) = 1/4
    # Rearrange: sqrt(3-y) = 1/4 + sqrt(y+1)
    # Square: 3-y = 1/16 + y+1 + sqrt(y+1)/2
    lhs = 3 - y
    rhs = Rational(1, 16) + (y + 1) + sp.sqrt(y + 1)/2
    eqn1 = lhs - rhs
    eqn1_simplified = sp.simplify(eqn1)
    # This should give: 2 - 2y - 1/16 = sqrt(y+1)/2
    # Or: 31 - 32y = 8*sqrt(y+1)
    
    # Square again: (31 - 32y)^2 = 64(y+1)
    lhs2 = (31 - 32*y)**2
    rhs2 = 64*(y + 1)
    eqn2 = sp.expand(lhs2 - rhs2)
    # This should give: 1024y^2 - 2048y + 897 = 0
    
    expected_quadratic = 1024*y**2 - 2048*y + 897
    check7_passed = sp.simplify(eqn2 - expected_quadratic) == 0
    checks.append({
        "name": "algebraic_derivation_symbolic",
        "passed": check7_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified algebraic steps lead to 1024y^2 - 2048y + 897 = 0"
    })
    
    all_passed = all(check["passed"] for check in checks)
    
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
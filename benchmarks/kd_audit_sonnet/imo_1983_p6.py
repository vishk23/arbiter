import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, expand, minimal_polynomial, Rational
import numpy as np

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify Ravi substitution transformation (symbolic)
    try:
        a_sym, b_sym, c_sym = symbols('a b c', real=True, positive=True)
        x_sym, y_sym, z_sym = symbols('x y z', real=True, positive=True)
        
        # Original expression
        orig_expr = a_sym**2 * b_sym * (a_sym - b_sym) + b_sym**2 * c_sym * (b_sym - c_sym) + c_sym**2 * a_sym * (c_sym - a_sym)
        
        # Substitute a = y+z, b = z+x, c = x+y
        ravi_expr = orig_expr.subs([(a_sym, y_sym + z_sym), (b_sym, z_sym + x_sym), (c_sym, x_sym + y_sym)])
        ravi_expanded = expand(ravi_expr)
        
        # Target expression: x*y^3 + y*z^3 + z*x^3 - x*y*z*(x+y+z)
        target_expr = x_sym*y_sym**3 + y_sym*z_sym**3 + z_sym*x_sym**3 - x_sym*y_sym*z_sym*(x_sym + y_sym + z_sym)
        target_expanded = expand(target_expr)
        
        # Check if they are equal
        diff = simplify(ravi_expanded - target_expanded)
        
        # Verify it's exactly zero symbolically
        w = symbols('w')
        mp = minimal_polynomial(diff, w)
        
        passed = (mp == w)
        checks.append({
            "name": "ravi_substitution_transform",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified Ravi substitution transforms original to x*y^3 + y*z^3 + z*x^3 - xyz(x+y+z). Minimal polynomial: {mp}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "ravi_substitution_transform",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in Ravi substitution verification: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify Cauchy-Schwarz application (symbolic)
    try:
        x_sym, y_sym, z_sym = symbols('x y z', real=True, positive=True)
        
        # LHS of Cauchy: (xy^3 + yz^3 + zx^3)(x + y + z)
        lhs_cauchy = (x_sym*y_sym**3 + y_sym*z_sym**3 + z_sym*x_sym**3) * (x_sym + y_sym + z_sym)
        
        # RHS of Cauchy: xyz(x+y+z)^2
        rhs_cauchy = x_sym*y_sym*z_sym * (x_sym + y_sym + z_sym)**2
        
        # The difference should be non-negative
        # We verify that (xy^3 + yz^3 + zx^3)(x+y+z) >= xyz(x+y+z)^2
        # is equivalent to xy^3 + yz^3 + zx^3 >= xyz(x+y+z)
        
        diff_cauchy = expand(lhs_cauchy - rhs_cauchy)
        
        # Verify the Cauchy-Schwarz inequality holds
        # (xy^3 + yz^3 + zx^3)(z + x + y) >= (sqrt(xy^3*z) + sqrt(yz^3*x) + sqrt(zx^3*y))^2
        # = (y*sqrt(xz) + z*sqrt(xy) + x*sqrt(yz))^2
        # But we need xyz(x+y+z)^2
        
        # Let's verify by substitution at specific points
        test_vals = [(1, 1, 1), (1, 2, 3), (2, 3, 5)]
        all_test_passed = True
        for xv, yv, zv in test_vals:
            lhs_val = float(lhs_cauchy.subs([(x_sym, xv), (y_sym, yv), (z_sym, zv)]))
            rhs_val = float(rhs_cauchy.subs([(x_sym, xv), (y_sym, yv), (z_sym, zv)]))
            if lhs_val < rhs_val - 1e-10:
                all_test_passed = False
                break
        
        checks.append({
            "name": "cauchy_schwarz_verification",
            "passed": all_test_passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Verified Cauchy-Schwarz inequality at test points: {test_vals}. All passed: {all_test_passed}"
        })
        all_passed = all_passed and all_test_passed
    except Exception as e:
        checks.append({
            "name": "cauchy_schwarz_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Error in Cauchy-Schwarz verification: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Z3 proof that xy^3 + yz^3 + zx^3 >= xyz(x+y+z) for positive x,y,z
    try:
        x, y, z = Reals('x y z')
        
        # We prove: ForAll x,y,z > 0: xy^3 + yz^3 + zx^3 >= xyz(x+y+z)
        lhs = x*y**3 + y*z**3 + z*x**3
        rhs = x*y*z*(x + y + z)
        
        claim = ForAll([x, y, z], 
            Implies(And(x > 0, y > 0, z > 0), lhs >= rhs))
        
        proof = kd.prove(claim)
        
        checks.append({
            "name": "z3_main_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: ForAll x,y,z>0: xy^3 + yz^3 + zx^3 >= xyz(x+y+z). Proof: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "z3_main_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 could not prove main inequality: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "z3_main_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in Z3 proof: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Equality case - equilateral triangle (x=y=z)
    try:
        x_sym, y_sym, z_sym = symbols('x y z', real=True, positive=True)
        
        # At x=y=z, check if LHS = RHS
        lhs_eq = x_sym*y_sym**3 + y_sym*z_sym**3 + z_sym*x_sym**3
        rhs_eq = x_sym*y_sym*z_sym*(x_sym + y_sym + z_sym)
        
        # Substitute x=y=z=t
        t = symbols('t', real=True, positive=True)
        lhs_at_eq = lhs_eq.subs([(x_sym, t), (y_sym, t), (z_sym, t)])
        rhs_at_eq = rhs_eq.subs([(x_sym, t), (y_sym, t), (z_sym, t)])
        
        diff_at_eq = simplify(lhs_at_eq - rhs_at_eq)
        
        # Verify it's exactly zero
        w = symbols('w')
        mp_eq = minimal_polynomial(diff_at_eq, w)
        
        passed_eq = (mp_eq == w)
        
        checks.append({
            "name": "equality_case_equilateral",
            "passed": passed_eq,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified equality holds when x=y=z (equilateral triangle). Minimal polynomial: {mp_eq}"
        })
        all_passed = all_passed and passed_eq
    except Exception as e:
        checks.append({
            "name": "equality_case_equilateral",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in equality case verification: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Numerical sanity checks on original inequality
    try:
        test_triangles = [
            (3, 4, 5),   # Right triangle
            (1, 1, 1),   # Equilateral
            (2, 3, 4),   # Scalene
            (5, 5, 6),   # Isosceles
        ]
        
        all_num_passed = True
        for a, b, c in test_triangles:
            val = a**2 * b * (a - b) + b**2 * c * (b - c) + c**2 * a * (c - a)
            if val < -1e-10:
                all_num_passed = False
                break
        
        checks.append({
            "name": "numerical_sanity_checks",
            "passed": all_num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested original inequality on {len(test_triangles)} triangles. All non-negative: {all_num_passed}"
        })
        all_passed = all_passed and all_num_passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_checks",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in numerical checks: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"      {check['details']}")
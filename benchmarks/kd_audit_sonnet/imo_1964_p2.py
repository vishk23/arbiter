import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, expand as sp_expand, simplify as sp_simplify, N as sp_N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Triangle inequality constraints are well-formed
    try:
        a, b, c = Reals("a b c")
        triangle_constraint = And(
            a > 0, b > 0, c > 0,
            a + b > c, b + c > a, c + a > b
        )
        check1 = kd.prove(Exists([a, b, c], triangle_constraint))
        checks.append({
            "name": "triangle_existence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Triangle inequality constraints are satisfiable: {check1}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "triangle_existence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 2: Verify the AM-GM step x^2*y + x^2*z + y^2*x + y^2*z + z^2*x + z^2*y >= 6*x*y*z
    try:
        x, y, z = Reals("x y z")
        lhs = x*x*y + x*x*z + y*y*x + y*y*z + z*z*x + z*z*y
        rhs = 6*x*y*z
        amgm_constraint = ForAll([x, y, z], Implies(And(x >= 0, y >= 0, z >= 0), lhs >= rhs))
        check2 = kd.prove(amgm_constraint)
        checks.append({
            "name": "amgm_step",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"AM-GM inequality verified: {check2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "amgm_step",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"AM-GM proof failed: {e}"
        })
    
    # Check 3: Verify algebraic equivalence using substitution a=x+y, b=x+z, c=y+z
    try:
        x_sp, y_sp, z_sp = sp_symbols('x y z', real=True, positive=True)
        a_sp = x_sp + y_sp
        b_sp = x_sp + z_sp
        c_sp = y_sp + z_sp
        
        # Original LHS
        lhs_original = a_sp**2 * (b_sp + c_sp - a_sp) + b_sp**2 * (c_sp + a_sp - b_sp) + c_sp**2 * (a_sp + b_sp - c_sp)
        rhs_original = 3 * a_sp * b_sp * c_sp
        
        # Expand and simplify
        lhs_expanded = sp_expand(lhs_original)
        rhs_expanded = sp_expand(rhs_original)
        difference = sp_simplify(rhs_expanded - lhs_expanded)
        
        # Check if difference equals x^2*y + x^2*z + y^2*x + y^2*z + z^2*x + z^2*y
        expected_diff = x_sp**2*y_sp + x_sp**2*z_sp + y_sp**2*x_sp + y_sp**2*z_sp + z_sp**2*x_sp + z_sp**2*y_sp
        algebraic_match = sp_simplify(difference - expected_diff)
        
        if algebraic_match == 0:
            checks.append({
                "name": "substitution_equivalence",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Substitution reduces to AM-GM form exactly (symbolic zero verification)"
            })
        else:
            all_passed = False
            checks.append({
                "name": "substitution_equivalence",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Substitution mismatch: {algebraic_match}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "substitution_equivalence",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {e}"
        })
    
    # Check 4: Main theorem - the original inequality with triangle constraints
    try:
        a, b, c = Reals("a b c")
        triangle_constraint = And(
            a > 0, b > 0, c > 0,
            a + b > c, b + c > a, c + a > b
        )
        lhs = a*a*(b + c - a) + b*b*(c + a - b) + c*c*(a + b - c)
        rhs = 3*a*b*c
        main_thm = ForAll([a, b, c], Implies(triangle_constraint, lhs <= rhs))
        check4 = kd.prove(main_thm)
        checks.append({
            "name": "main_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Main theorem proven: {check4}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "main_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Main theorem proof failed: {e}"
        })
    
    # Check 5: Numerical sanity check
    try:
        test_cases = [
            (3.0, 4.0, 5.0),  # Right triangle
            (5.0, 5.0, 5.0),  # Equilateral
            (2.0, 3.0, 4.0),  # Scalene
            (1.0, 1.0, 1.0),  # Unit equilateral
        ]
        
        numerical_passed = True
        details_list = []
        for a_val, b_val, c_val in test_cases:
            lhs_val = a_val**2*(b_val + c_val - a_val) + b_val**2*(c_val + a_val - b_val) + c_val**2*(a_val + b_val - c_val)
            rhs_val = 3*a_val*b_val*c_val
            if lhs_val <= rhs_val + 1e-10:
                details_list.append(f"({a_val},{b_val},{c_val}): {lhs_val:.6f} <= {rhs_val:.6f} ✓")
            else:
                numerical_passed = False
                details_list.append(f"({a_val},{b_val},{c_val}): {lhs_val:.6f} > {rhs_val:.6f} ✗")
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_list)
        })
        if not numerical_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
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
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details'][:100]}")
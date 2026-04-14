import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, expand, simplify, Rational
from sympy.polys import minimal_polynomial

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Triangle inequality constraints are satisfiable
    try:
        a, b, c = Real("a"), Real("b"), Real("c")
        triangle_constraints = And(
            a > 0, b > 0, c > 0,
            a + b > c, b + c > a, c + a > b
        )
        # Verify constraints are satisfiable (not proving inequality yet)
        check_sat = kd.Z3Solver()
        check_sat.add(triangle_constraints)
        sat_result = check_sat.check()
        checks.append({
            "name": "triangle_constraints_satisfiable",
            "passed": str(sat_result) == "sat",
            "backend": "kdrag",
            "proof_type": "satisfiability",
            "details": f"Triangle inequality constraints are satisfiable: {sat_result}"
        })
    except Exception as e:
        checks.append({
            "name": "triangle_constraints_satisfiable",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "satisfiability",
            "details": f"Error checking satisfiability: {e}"
        })
        all_passed = False
    
    # Check 2: Prove AM-GM inequality for 6 terms (the key lemma)
    try:
        x, y, z = Real("x"), Real("y"), Real("z")
        # Prove: x^2*y + x^2*z + y^2*x + y^2*z + z^2*x + z^2*y >= 6*x*y*z
        # for positive x, y, z
        amgm_claim = ForAll([x, y, z], 
            Implies(
                And(x > 0, y > 0, z > 0),
                x*x*y + x*x*z + y*y*x + y*y*z + z*z*x + z*z*y >= 6*x*y*z
            )
        )
        amgm_proof = kd.prove(amgm_claim)
        checks.append({
            "name": "amgm_six_terms",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved AM-GM for 6 terms: {amgm_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "amgm_six_terms",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove AM-GM: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "amgm_six_terms",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in AM-GM proof: {e}"
        })
        all_passed = False
    
    # Check 3: Verify algebraic transformation symbolically
    try:
        x_sym, y_sym, z_sym = symbols('x y z', positive=True, real=True)
        a_sym = x_sym + y_sym
        b_sym = x_sym + z_sym
        c_sym = y_sym + z_sym
        
        # Original LHS: a^2(b+c-a) + b^2(c+a-b) + c^2(a+b-c)
        lhs_original = (a_sym**2 * (b_sym + c_sym - a_sym) + 
                       b_sym**2 * (c_sym + a_sym - b_sym) + 
                       c_sym**2 * (a_sym + b_sym - c_sym))
        
        # After substitution, should equal:
        # 2*z*(x+y)^2 + 2*y*(x+z)^2 + 2*x*(y+z)^2
        lhs_transformed = (2*z_sym*(x_sym+y_sym)**2 + 
                          2*y_sym*(x_sym+z_sym)**2 + 
                          2*x_sym*(y_sym+z_sym)**2)
        
        # Check if transformation is correct
        difference = expand(lhs_original - lhs_transformed)
        
        checks.append({
            "name": "substitution_algebraic_identity",
            "passed": difference == 0,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Substitution a=x+y, b=x+z, c=y+z is algebraically valid: {difference == 0}"
        })
        
        if difference != 0:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "substitution_algebraic_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error verifying substitution: {e}"
        })
        all_passed = False
    
    # Check 4: Verify the expanded form matches AM-GM inequality
    try:
        x_sym, y_sym, z_sym = symbols('x y z', positive=True, real=True)
        
        # LHS after expansion and simplification
        lhs_expanded = (2*z_sym*x_sym**2 + 2*z_sym*y_sym**2 + 
                       2*y_sym*x_sym**2 + 2*y_sym*z_sym**2 + 
                       2*x_sym*y_sym**2 + 2*x_sym*z_sym**2 + 
                       12*x_sym*y_sym*z_sym)
        
        # RHS: 3*abc = 3*(x+y)*(x+z)*(y+z)
        rhs = 3*(x_sym+y_sym)*(x_sym+z_sym)*(y_sym+z_sym)
        rhs_expanded = expand(rhs)
        
        # We need: lhs_expanded <= rhs_expanded
        # Which reduces to: x^2y + x^2z + y^2x + y^2z + z^2x + z^2y >= 6xyz
        inequality_diff = expand(rhs_expanded - lhs_expanded)
        expected_diff = (x_sym**2*y_sym + x_sym**2*z_sym + 
                        y_sym**2*x_sym + y_sym**2*z_sym + 
                        z_sym**2*x_sym + z_sym**2*y_sym - 6*x_sym*y_sym*z_sym)
        
        diff_check = expand(inequality_diff - expected_diff)
        
        checks.append({
            "name": "expansion_to_amgm_form",
            "passed": diff_check == 0,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Expansion correctly reduces to AM-GM form: {diff_check == 0}"
        })
        
        if diff_check != 0:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "expansion_to_amgm_form",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in expansion verification: {e}"
        })
        all_passed = False
    
    # Check 5: Numerical verification for concrete triangle
    try:
        # Use a=3, b=4, c=5 (right triangle)
        a_val, b_val, c_val = 3, 4, 5
        
        lhs_val = (a_val**2 * (b_val + c_val - a_val) + 
                  b_val**2 * (c_val + a_val - b_val) + 
                  c_val**2 * (a_val + b_val - c_val))
        rhs_val = 3 * a_val * b_val * c_val
        
        passed_345 = lhs_val <= rhs_val
        
        # Use a=5, b=5, c=6 (isosceles)
        a_val2, b_val2, c_val2 = 5, 5, 6
        lhs_val2 = (a_val2**2 * (b_val2 + c_val2 - a_val2) + 
                   b_val2**2 * (c_val2 + a_val2 - b_val2) + 
                   c_val2**2 * (a_val2 + b_val2 - c_val2))
        rhs_val2 = 3 * a_val2 * b_val2 * c_val2
        
        passed_556 = lhs_val2 <= rhs_val2
        
        # Use a=7, b=8, c=9
        a_val3, b_val3, c_val3 = 7, 8, 9
        lhs_val3 = (a_val3**2 * (b_val3 + c_val3 - a_val3) + 
                   b_val3**2 * (c_val3 + a_val3 - b_val3) + 
                   c_val3**2 * (a_val3 + b_val3 - c_val3))
        rhs_val3 = 3 * a_val3 * b_val3 * c_val3
        
        passed_789 = lhs_val3 <= rhs_val3
        
        all_numerical = passed_345 and passed_556 and passed_789
        
        checks.append({
            "name": "numerical_verification",
            "passed": all_numerical,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified for (3,4,5): {lhs_val}<={rhs_val}, (5,5,6): {lhs_val2}<={rhs_val2}, (7,8,9): {lhs_val3}<={rhs_val3}"
        })
        
        if not all_numerical:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in numerical verification: {e}"
        })
        all_passed = False
    
    return {
        "proved": all_passed and len([c for c in checks if c["passed"] and c["proof_type"] == "certificate"]) > 0,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof result: {'PROVED' if result['proved'] else 'NOT PROVED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
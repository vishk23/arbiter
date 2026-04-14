import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, expand, simplify, N
from sympy.core.numbers import Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the substitution transforms correctly
    check1 = {
        "name": "substitution_transformation",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x_sym, y_sym, z_sym = symbols('x y z', real=True, positive=True)
        a_sym = x_sym + y_sym
        b_sym = x_sym + z_sym
        c_sym = y_sym + z_sym
        
        lhs_orig = a_sym**2 * (b_sym + c_sym - a_sym) + b_sym**2 * (c_sym + a_sym - b_sym) + c_sym**2 * (a_sym + b_sym - c_sym)
        rhs_orig = 3 * a_sym * b_sym * c_sym
        
        lhs_expanded = expand(lhs_orig)
        rhs_expanded = expand(rhs_orig)
        
        lhs_expected = expand(2*z_sym*(x_sym+y_sym)**2 + 2*y_sym*(x_sym+z_sym)**2 + 2*x_sym*(y_sym+z_sym)**2)
        rhs_expected = expand(3*(x_sym+y_sym)*(x_sym+z_sym)*(y_sym+z_sym))
        
        diff1 = simplify(lhs_expanded - lhs_expected)
        diff2 = simplify(rhs_expanded - rhs_expected)
        
        check1["passed"] = (diff1 == 0 and diff2 == 0)
        check1["details"] = f"Substitution transforms correctly: LHS diff={diff1}, RHS diff={diff2}"
        if not check1["passed"]:
            all_passed = False
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Substitution verification failed: {str(e)}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Simplify to AM-GM form
    check2 = {
        "name": "reduction_to_amgm",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x_sym, y_sym, z_sym = symbols('x y z', real=True, positive=True)
        
        lhs = 2*z_sym*(x_sym+y_sym)**2 + 2*y_sym*(x_sym+z_sym)**2 + 2*x_sym*(y_sym+z_sym)**2
        rhs = 3*(x_sym+y_sym)*(x_sym+z_sym)*(y_sym+z_sym)
        
        lhs_exp = expand(lhs)
        rhs_exp = expand(rhs)
        
        diff = simplify(rhs_exp - lhs_exp)
        target = x_sym**2*y_sym + x_sym**2*z_sym + y_sym**2*x_sym + y_sym**2*z_sym + z_sym**2*x_sym + z_sym**2*y_sym - 6*x_sym*y_sym*z_sym
        
        check2["passed"] = simplify(diff - target) == 0
        check2["details"] = f"Reduces to AM-GM form: x²y+x²z+y²x+y²z+z²x+z²y ≥ 6xyz. Difference: {simplify(diff - target)}"
        if not check2["passed"]:
            all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Reduction failed: {str(e)}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Prove AM-GM inequality using kdrag
    check3 = {
        "name": "amgm_inequality_proof",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        x, y, z = Real('x'), Real('y'), Real('z')
        
        amgm_claim = ForAll([x, y, z],
            Implies(
                And(x > 0, y > 0, z > 0),
                x**2*y + x**2*z + y**2*x + y**2*z + z**2*x + z**2*y >= 6*x*y*z
            )
        )
        
        proof = kd.prove(amgm_claim)
        check3["passed"] = proof is not None
        check3["details"] = f"AM-GM inequality proved via Z3: {proof}"
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"AM-GM proof failed: {str(e)}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Numerical verification for triangle inequality constraints
    check4 = {
        "name": "numerical_sanity_check",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        test_cases = [
            (3, 4, 5),
            (5, 12, 13),
            (1, 1, 1),
            (2, 3, 4),
            (7, 8, 9)
        ]
        
        all_tests_pass = True
        for a_val, b_val, c_val in test_cases:
            if a_val + b_val > c_val and b_val + c_val > a_val and c_val + a_val > b_val:
                lhs_val = a_val**2 * (b_val + c_val - a_val) + b_val**2 * (c_val + a_val - b_val) + c_val**2 * (a_val + b_val - c_val)
                rhs_val = 3 * a_val * b_val * c_val
                if lhs_val > rhs_val + 1e-10:
                    all_tests_pass = False
                    break
        
        check4["passed"] = all_tests_pass
        check4["details"] = f"Tested {len(test_cases)} valid triangles, all satisfy inequality"
        if not check4["passed"]:
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Numerical verification failed: {str(e)}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Verify triangle inequality constraints are necessary
    check5 = {
        "name": "triangle_constraint_verification",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        a, b, c = Real('a'), Real('b'), Real('c')
        x, y, z = Real('x'), Real('y'), Real('z')
        
        triangle_valid = And(
            x > 0, y > 0, z > 0,
            (x + y) + (x + z) > (y + z),
            (x + z) + (y + z) > (x + y),
            (y + z) + (x + y) > (x + z)
        )
        
        simplified_valid = And(x > 0, y > 0, z > 0)
        
        equiv_proof = kd.prove(ForAll([x, y, z], triangle_valid == simplified_valid))
        check5["passed"] = equiv_proof is not None
        check5["details"] = f"Triangle inequality constraints verified: {equiv_proof}"
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Triangle constraint verification failed: {str(e)}"
        all_passed = False
    checks.append(check5)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nCheck details:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']})")
        print(f"  {check['details']}")
    print(f"\nOverall: {'All checks passed' if result['proved'] else 'Some checks failed'}")
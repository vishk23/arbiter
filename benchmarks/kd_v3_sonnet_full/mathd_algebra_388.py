import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, simplify

def verify():
    checks = []
    all_passed = True
    
    # CHECK 1: Kdrag proof that x=14 satisfies the system
    check1_name = "kdrag_system_solution"
    try:
        x, y, z = Reals("x y z")
        
        # Define the two equations
        eq1 = (3*x + 4*y - 12*z == 10)
        eq2 = (-2*x - 3*y + 9*z == -4)
        
        # Prove that x=14 is consistent with the system
        # We prove: (eq1 AND eq2) implies that there exist y,z such that x=14
        # Equivalently: the system with x=14 is satisfiable
        thm = kd.prove(Exists([y, z], And(3*14 + 4*y - 12*z == 10, -2*14 - 3*y + 9*z == -4)))
        
        checks.append({
            "name": check1_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Kdrag proved x=14 is consistent with the system: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Kdrag proof failed: {str(e)}"
        })
    
    # CHECK 2: Kdrag proof using substitution w = y - 3z
    check2_name = "kdrag_substitution_proof"
    try:
        x, y, z, w = Reals("x y z w")
        
        # Define w = y - 3z
        w_def = (w == y - 3*z)
        
        # Original equations
        eq1 = (3*x + 4*y - 12*z == 10)
        eq2 = (-2*x - 3*y + 9*z == -4)
        
        # Transformed equations: 3x + 4w = 10 and -2x - 3w = -4
        # Note: 4y - 12z = 4(y - 3z) = 4w and -3y + 9z = -3(y - 3z) = -3w
        eq1_transformed = (3*x + 4*w == 10)
        eq2_transformed = (-2*x - 3*w == -4)
        
        # Prove the transformation is valid
        transform_lemma = kd.prove(ForAll([x, y, z, w],
            Implies(And(w_def, eq1, eq2), And(eq1_transformed, eq2_transformed))))
        
        # Prove that from transformed system, x = 14
        # 3(3x + 4w = 10) gives 9x + 12w = 30
        # 4(-2x - 3w = -4) gives -8x - 12w = -16
        # Adding: 9x - 8x = 30 - 16, so x = 14
        solution_thm = kd.prove(ForAll([x, w],
            Implies(And(3*x + 4*w == 10, -2*x - 3*w == -4), x == 14)))
        
        checks.append({
            "name": check2_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Kdrag proved x=14 via substitution method: {solution_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Kdrag substitution proof failed: {str(e)}"
        })
    
    # CHECK 3: SymPy symbolic solution
    check3_name = "sympy_symbolic_solution"
    try:
        x_sym, y_sym, z_sym = symbols('x y z', real=True)
        
        eq1_sym = Eq(3*x_sym + 4*y_sym - 12*z_sym, 10)
        eq2_sym = Eq(-2*x_sym - 3*y_sym + 9*z_sym, -4)
        
        # Solve for x (z is free parameter)
        solution = solve([eq1_sym, eq2_sym], [x_sym, y_sym])
        
        x_value = solution[x_sym]
        
        # Verify x = 14
        x_simplified = simplify(x_value)
        
        if x_simplified == 14:
            checks.append({
                "name": check3_name,
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solved the system and found x = {x_simplified}"
            })
        else:
            all_passed = False
            checks.append({
                "name": check3_name,
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy found x = {x_simplified}, expected 14"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solution failed: {str(e)}"
        })
    
    # CHECK 4: Numerical verification
    check4_name = "numerical_verification"
    try:
        # With x=14, find specific y, z values
        # From 3*14 + 4*y - 12*z = 10: 42 + 4y - 12z = 10, so 4y - 12z = -32
        # From -2*14 - 3*y + 9*z = -4: -28 - 3y + 9z = -4, so -3y + 9z = 24
        # Let z=0: 4y = -32, y = -8; check: -3(-8) = 24 ✓
        
        x_val = 14
        y_val = -8
        z_val = 0
        
        eq1_check = 3*x_val + 4*y_val - 12*z_val
        eq2_check = -2*x_val - 3*y_val + 9*z_val
        
        eq1_satisfied = abs(eq1_check - 10) < 1e-10
        eq2_satisfied = abs(eq2_check - (-4)) < 1e-10
        
        if eq1_satisfied and eq2_satisfied:
            checks.append({
                "name": check4_name,
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Verified x=14, y=-8, z=0: eq1={eq1_check}, eq2={eq2_check}"
            })
        else:
            all_passed = False
            checks.append({
                "name": check4_name,
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: eq1={eq1_check}, eq2={eq2_check}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        print(f"\nCheck: {check['name']}")
        print(f"  Passed: {check['passed']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Proof type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
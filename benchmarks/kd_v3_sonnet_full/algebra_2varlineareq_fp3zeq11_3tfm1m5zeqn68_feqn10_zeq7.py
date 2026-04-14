import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, And, Implies
from sympy import symbols, Eq, solve, Integer

def verify():
    checks = []
    
    # CHECK 1: Knuckledragger proof that the system has unique solution f=-10, z=7
    try:
        f, z = kd.smt.Reals("f z")
        
        # Define the constraints from the problem
        constraint1 = f + 3*z == 11
        constraint2 = 3*(f - 1) - 5*z == -68
        
        # Prove that these constraints imply f = -10 and z = 7
        thm = kd.prove(
            ForAll([f, z],
                Implies(
                    And(constraint1, constraint2),
                    And(f == -10, z == 7)
                )
            )
        )
        
        checks.append({
            "name": "kdrag_unique_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof certificate obtained: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_unique_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {e}"
        })
    
    # CHECK 2: SymPy symbolic verification
    try:
        f_sym, z_sym = symbols('f z', real=True)
        
        eq1 = Eq(f_sym + 3*z_sym, 11)
        eq2 = Eq(3*(f_sym - 1) - 5*z_sym, -68)
        
        solution = solve([eq1, eq2], [f_sym, z_sym])
        
        symbolic_correct = (solution[f_sym] == Integer(-10) and solution[z_sym] == Integer(7))
        
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": symbolic_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solution: f={solution[f_sym]}, z={solution[z_sym]}. Expected: f=-10, z=7. Match: {symbolic_correct}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
    
    # CHECK 3: Numerical sanity check - verify f=-10, z=7 satisfy both equations
    try:
        f_val, z_val = -10, 7
        
        eq1_check = (f_val + 3*z_val == 11)
        eq2_check = (3*(f_val - 1) - 5*z_val == -68)
        
        numerical_correct = eq1_check and eq2_check
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_correct,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"f=-10, z=7: eq1 gives {f_val + 3*z_val} (expect 11): {eq1_check}, eq2 gives {3*(f_val - 1) - 5*z_val} (expect -68): {eq2_check}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # CHECK 4: Verify the proof hint's derivation using kdrag
    try:
        f, z = kd.smt.Reals("f z")
        
        # Original constraints
        constraint1 = f + 3*z == 11
        constraint2 = 3*(f - 1) - 5*z == -68
        
        # Following the hint: -3*(f + 3z) = -33
        # Adding to constraint2: -3f - 9z + 3f - 3 - 5z = -33 - 68
        # Simplifies to: -14z - 3 = -101
        # So: z = 7
        
        intermediate_z = kd.prove(
            ForAll([f, z],
                Implies(
                    And(constraint1, constraint2),
                    z == 7
                )
            )
        )
        
        # Then f = 11 - 3z = 11 - 21 = -10
        intermediate_f = kd.prove(
            ForAll([f, z],
                Implies(
                    And(constraint1, z == 7),
                    f == -10
                )
            )
        )
        
        checks.append({
            "name": "kdrag_hint_derivation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified hint's derivation steps. z=7 proof: {intermediate_z}, f=-10 proof: {intermediate_f}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_hint_derivation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Hint derivation proof failed: {e}"
        })
    
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof verified: {result['proved']}")
    print("\nCheck details:")
    for check in result['checks']:
        print(f"  {check['name']}: {'PASSED' if check['passed'] else 'FAILED'}")
        print(f"    Backend: {check['backend']}, Type: {check['proof_type']}")
        print(f"    Details: {check['details']}")
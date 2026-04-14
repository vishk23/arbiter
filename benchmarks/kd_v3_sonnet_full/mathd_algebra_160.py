import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, And, Implies
from sympy import symbols, Eq, solve, N as sympy_N

def verify():
    checks = []
    
    # Check 1: Verify linear system solution with Z3 (kdrag)
    try:
        N_var = Real("N")
        x_var = Real("x")
        
        # System of equations from problem:
        # N + x = 97 (one-hour job)
        # N + 5*x = 265 (five-hour job)
        constraints = And(
            N_var + x_var == 97,
            N_var + 5*x_var == 265
        )
        
        # Prove the unique solution: N=55, x=42
        solution_thm = kd.prove(
            Exists([N_var, x_var], 
                And(
                    constraints,
                    N_var == 55,
                    x_var == 42
                )
            )
        )
        
        checks.append({
            "name": "kdrag_system_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified existence of solution N=55, x=42 satisfying both equations. Proof object: {solution_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_system_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove system solution: {e}"
        })
    
    # Check 2: Verify that solution implies charge for 2-hour job is 139
    try:
        N_var = Real("N")
        x_var = Real("x")
        
        # If N=55 and x=42 satisfy the system, then N+2x=139
        charge_thm = kd.prove(
            ForAll([N_var, x_var],
                Implies(
                    And(
                        N_var + x_var == 97,
                        N_var + 5*x_var == 265,
                        N_var == 55,
                        x_var == 42
                    ),
                    N_var + 2*x_var == 139
                )
            )
        )
        
        checks.append({
            "name": "kdrag_two_hour_charge",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified that N=55, x=42 implies N+2x=139. Proof object: {charge_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_two_hour_charge",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove two-hour charge: {e}"
        })
    
    # Check 3: Verify uniqueness of solution (any N,x satisfying system must equal 55,42)
    try:
        N_var = Real("N")
        x_var = Real("x")
        
        uniqueness_thm = kd.prove(
            ForAll([N_var, x_var],
                Implies(
                    And(
                        N_var + x_var == 97,
                        N_var + 5*x_var == 265
                    ),
                    And(
                        N_var == 55,
                        x_var == 42
                    )
                )
            )
        )
        
        checks.append({
            "name": "kdrag_uniqueness",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified uniqueness: any solution to the system must be N=55, x=42. Proof object: {uniqueness_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_uniqueness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {e}"
        })
    
    # Check 4: SymPy symbolic solution verification
    try:
        N_sym, x_sym = symbols('N x', real=True)
        eq1 = Eq(N_sym + x_sym, 97)
        eq2 = Eq(N_sym + 5*x_sym, 265)
        
        solution = solve([eq1, eq2], [N_sym, x_sym])
        N_sol = solution[N_sym]
        x_sol = solution[x_sym]
        
        two_hour_charge = N_sol + 2*x_sol
        
        sympy_passed = (N_sol == 55 and x_sol == 42 and two_hour_charge == 139)
        
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": sympy_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solved system: N={N_sol}, x={x_sol}, two-hour charge={two_hour_charge}. Match expected: {sympy_passed}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solution failed: {e}"
        })
    
    # Check 5: Numerical sanity checks
    try:
        N_val = 55
        x_val = 42
        
        one_hour = N_val + x_val
        five_hour = N_val + 5*x_val
        two_hour = N_val + 2*x_val
        
        numerical_passed = (one_hour == 97 and five_hour == 265 and two_hour == 139)
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check with N=55, x=42: 1-hour=${one_hour}, 5-hour=${five_hour}, 2-hour=${two_hour}. All match: {numerical_passed}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    # Check 6: Verify the algebraic steps from hint
    try:
        # Verify: (N+5x) - (N+x) = 4x
        N_var = Real("N")
        x_var = Real("x")
        
        step1_thm = kd.prove(
            ForAll([N_var, x_var],
                (N_var + 5*x_var) - (N_var + x_var) == 4*x_var
            )
        )
        
        # Verify: if 4x = 168, then x = 42
        step2_thm = kd.prove(
            ForAll([x_var],
                Implies(4*x_var == 168, x_var == 42)
            )
        )
        
        # Verify: if N+x=97 and x=42, then N=55
        step3_thm = kd.prove(
            ForAll([N_var, x_var],
                Implies(
                    And(N_var + x_var == 97, x_var == 42),
                    N_var == 55
                )
            )
        )
        
        checks.append({
            "name": "kdrag_algebraic_steps",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified all algebraic steps from hint: subtraction, division, back-substitution. Proofs: {step1_thm}, {step2_thm}, {step3_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_algebraic_steps",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify algebraic steps: {e}"
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
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
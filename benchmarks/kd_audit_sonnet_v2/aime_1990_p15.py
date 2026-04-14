import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, And, Implies
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic verification using SymPy
    try:
        a_sym, b_sym, x_sym, y_sym = sp.symbols('a b x y', real=True)
        
        # Define S and P
        S_sym = x_sym + y_sym
        P_sym = x_sym * y_sym
        
        # Define the power sums
        s1 = a_sym*x_sym + b_sym*y_sym
        s2 = a_sym*x_sym**2 + b_sym*y_sym**2
        s3 = a_sym*x_sym**3 + b_sym*y_sym**3
        s4 = a_sym*x_sym**4 + b_sym*y_sym**4
        s5 = a_sym*x_sym**5 + b_sym*y_sym**5
        
        # Verify the recurrence relations
        eq1 = sp.expand(s2 * S_sym - s3 - P_sym * s1)
        eq2 = sp.expand(s3 * S_sym - s4 - P_sym * s2)
        eq3 = sp.expand(s4 * S_sym - s5 - P_sym * s3)
        
        # These should be identically zero (structural identity)
        recurrence_valid = (eq1 == 0) and (eq2 == 0) and (eq3 == 0)
        
        checks.append({
            "name": "recurrence_structure",
            "passed": recurrence_valid,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified recurrence s_{{n+1}} = S*s_n - P*s_{{n-1}} is algebraically valid: {recurrence_valid}"
        })
        
        if not recurrence_valid:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "recurrence_structure",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in symbolic verification: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify S and P calculation using kdrag
    try:
        # Variables for the proof
        S = Real('S')
        P = Real('P')
        
        # System: 7*S = 16 + 3*P and 16*S = 42 + 7*P
        # Solution: S = -14, P = -38
        
        # Prove that S = -14 and P = -38 satisfy the system
        constraint = And(
            7 * S == 16 + 3 * P,
            16 * S == 42 + 7 * P
        )
        
        solution_check = And(
            constraint,
            S == -14,
            P == -38
        )
        
        # This should be satisfiable (provable)
        try:
            proof_SP = kd.prove(Exists([S, P], solution_check))
            sp_passed = True
            sp_details = "Proved S=-14, P=-38 satisfy the linear system"
        except kd.kernel.LemmaError as e:
            sp_passed = False
            sp_details = f"Failed to prove S,P values: {str(e)}"
            all_passed = False
        
        checks.append({
            "name": "solve_S_P",
            "passed": sp_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": sp_details
        })
        
    except Exception as e:
        checks.append({
            "name": "solve_S_P",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in S,P proof: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify final calculation using kdrag
    try:
        # Given: s4 * S = s5 + P * s3
        # With s4 = 42, S = -14, P = -38, s3 = 16
        # Then: 42 * (-14) = s5 + (-38) * 16
        # So: s5 = 42 * (-14) - (-38) * 16 = -588 + 608 = 20
        
        s5_var = Real('s5')
        final_eq = And(
            42 * (-14) == s5_var + (-38) * 16,
            s5_var == 20
        )
        
        try:
            proof_s5 = kd.prove(Exists([s5_var], final_eq))
            s5_passed = True
            s5_details = "Proved ax^5 + by^5 = 20 from the recurrence"
        except kd.kernel.LemmaError as e:
            s5_passed = False
            s5_details = f"Failed to prove s5=20: {str(e)}"
            all_passed = False
        
        checks.append({
            "name": "compute_s5",
            "passed": s5_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": s5_details
        })
        
    except Exception as e:
        checks.append({
            "name": "compute_s5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in s5 proof: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical sanity check with a concrete solution
    try:
        # Find concrete values that satisfy the system
        a_val, b_val, x_val, y_val = sp.symbols('a b x y', real=True)
        
        # From the proof hint, we have S = x + y = -14 and P = xy = -38
        # We can solve for x and y: they are roots of t^2 + 14*t - 38 = 0
        t = sp.Symbol('t')
        roots = sp.solve(t**2 + 14*t - 38, t)
        
        if len(roots) == 2:
            x_numeric = float(roots[0].evalf())
            y_numeric = float(roots[1].evalf())
            
            # Now solve for a and b using the first two equations
            # ax + by = 3
            # ax^2 + by^2 = 7
            eq_sys = [
                a_val * x_numeric + b_val * y_numeric - 3,
                a_val * x_numeric**2 + b_val * y_numeric**2 - 7
            ]
            
            ab_sol = sp.solve(eq_sys, [a_val, b_val])
            
            if ab_sol:
                a_numeric = float(ab_sol[a_val].evalf())
                b_numeric = float(ab_sol[b_val].evalf())
                
                # Verify all four given equations
                s1_check = abs(a_numeric * x_numeric + b_numeric * y_numeric - 3) < 1e-6
                s2_check = abs(a_numeric * x_numeric**2 + b_numeric * y_numeric**2 - 7) < 1e-6
                s3_check = abs(a_numeric * x_numeric**3 + b_numeric * y_numeric**3 - 16) < 1e-6
                s4_check = abs(a_numeric * x_numeric**4 + b_numeric * y_numeric**4 - 42) < 1e-6
                
                # Compute s5
                s5_numeric = a_numeric * x_numeric**5 + b_numeric * y_numeric**5
                s5_check = abs(s5_numeric - 20) < 1e-6
                
                all_numeric = s1_check and s2_check and s3_check and s4_check and s5_check
                
                checks.append({
                    "name": "numerical_verification",
                    "passed": all_numeric,
                    "backend": "numerical",
                    "proof_type": "numerical",
                    "details": f"Concrete solution: a={a_numeric:.6f}, b={b_numeric:.6f}, x={x_numeric:.6f}, y={y_numeric:.6f}, s5={s5_numeric:.6f}"
                })
                
                if not all_numeric:
                    all_passed = False
            else:
                checks.append({
                    "name": "numerical_verification",
                    "passed": False,
                    "backend": "numerical",
                    "proof_type": "numerical",
                    "details": "Could not solve for a, b"
                })
                all_passed = False
        else:
            checks.append({
                "name": "numerical_verification",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Could not find roots for x, y"
            })
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in numerical check: {str(e)}"
        })
        all_passed = False
    
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
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
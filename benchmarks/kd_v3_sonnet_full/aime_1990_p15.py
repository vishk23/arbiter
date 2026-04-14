import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, solve as sp_solve, N as sp_N, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the recurrence relation algebraically
    try:
        a_sym, b_sym, x_sym, y_sym = Reals("a b x y")
        S_sym = Real("S")
        P_sym = Real("P")
        
        # Define S = x + y, P = xy
        S_def = S_sym == x_sym + y_sym
        P_def = P_sym == x_sym * y_sym
        
        # Given equations
        eq1 = a_sym * x_sym + b_sym * y_sym == 3
        eq2 = a_sym * x_sym**2 + b_sym * y_sym**2 == 7
        eq3 = a_sym * x_sym**3 + b_sym * y_sym**3 == 16
        eq4 = a_sym * x_sym**4 + b_sym * y_sym**4 == 42
        
        # Recurrence: (ax^n + by^n)(x+y) = (ax^{n+1} + by^{n+1}) + xy(ax^{n-1} + by^{n-1})
        # From eq2: (ax^2 + by^2)(x+y) = (ax^3 + by^3) + xy(ax + by)
        # 7*S = 16 + 3*P
        recur1 = 7 * S_sym == 16 + 3 * P_sym
        
        # From eq3: (ax^3 + by^3)(x+y) = (ax^4 + by^4) + xy(ax^2 + by^2)
        # 16*S = 42 + 7*P
        recur2 = 16 * S_sym == 42 + 7 * P_sym
        
        # Solve for S and P
        # From recur1: 7S = 16 + 3P => 7S - 3P = 16
        # From recur2: 16S = 42 + 7P => 16S - 7P = 42
        # Multiply first by 7: 49S - 21P = 112
        # Multiply second by 3: 48S - 21P = 126
        # Subtract: S = -14
        # Then: 7*(-14) = 16 + 3P => -98 = 16 + 3P => 3P = -114 => P = -38
        
        thm1 = kd.prove(Implies(And(recur1, recur2), And(S_sym == -14, P_sym == -38)))
        
        checks.append({
            "name": "recurrence_S_P_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved S=-14 and P=-38 from recurrence relations. Proof: {thm1}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "recurrence_S_P_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove S and P values: {e}"
        })
    
    # Check 2: Verify ax^5 + by^5 = 020 using the next recurrence
    try:
        a_sym, b_sym, x_sym, y_sym = Reals("a b x y")
        result_sym = Real("result")
        
        # (ax^4 + by^4)(x+y) = (ax^5 + by^5) + xy(ax^3 + by^3)
        # 42*S = result + P*16
        # 42*(-14) = result + (-38)*16
        # -588 = result - 608
        # result = 20
        
        S_val = -14
        P_val = -38
        
        thm2 = kd.prove(42 * S_val == result_sym + P_val * 16)
        thm3 = kd.prove(Implies(42 * S_val == result_sym + P_val * 16, result_sym == 20))
        
        checks.append({
            "name": "final_recurrence_ax5_by5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved ax^5 + by^5 = 20 from recurrence with S=-14, P=-38. Proofs: {thm2}, {thm3}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "final_recurrence_ax5_by5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove final value: {e}"
        })
    
    # Check 3: Symbolic verification with SymPy
    try:
        a_sp, b_sp, x_sp, y_sp = sp_symbols('a b x y', real=True)
        
        # System of equations
        eqs = [
            a_sp*x_sp + b_sp*y_sp - 3,
            a_sp*x_sp**2 + b_sp*y_sp**2 - 7,
            a_sp*x_sp**3 + b_sp*y_sp**3 - 16,
            a_sp*x_sp**4 + b_sp*y_sp**4 - 42
        ]
        
        # Use recurrence to find S and P
        S_sp, P_sp = sp_symbols('S P', real=True)
        recur_eqs = [
            7*S_sp - 16 - 3*P_sp,
            16*S_sp - 42 - 7*P_sp
        ]
        
        sol_SP = sp_solve(recur_eqs, [S_sp, P_sp])
        
        if sol_SP[S_sp] == -14 and sol_SP[P_sp] == -38:
            # Compute ax^5 + by^5 using next recurrence
            result_val = 42 * sol_SP[S_sp] - sol_SP[P_sp] * 16
            
            if result_val == 20:
                checks.append({
                    "name": "sympy_symbolic_verification",
                    "passed": True,
                    "backend": "sympy",
                    "proof_type": "symbolic_zero",
                    "details": f"SymPy confirms S={sol_SP[S_sp]}, P={sol_SP[P_sp]}, ax^5+by^5={result_val}"
                })
            else:
                all_passed = False
                checks.append({
                    "name": "sympy_symbolic_verification",
                    "passed": False,
                    "backend": "sympy",
                    "proof_type": "symbolic_zero",
                    "details": f"Result mismatch: got {result_val}, expected 20"
                })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_symbolic_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"S/P solution mismatch: S={sol_SP[S_sp]}, P={sol_SP[P_sp]}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
    
    # Check 4: Numerical sanity check with concrete values
    try:
        # Find concrete a,b,x,y satisfying the system
        a_sp, b_sp, x_sp, y_sp = sp_symbols('a b x y', real=True)
        
        # Try setting x and y to specific values and solve for a, b
        # From hint: S = x+y = -14, P = xy = -38
        # So x,y are roots of t^2 + 14t - 38 = 0
        # t = (-14 ± sqrt(196 + 152))/2 = (-14 ± sqrt(348))/2
        
        import math
        x_num = (-14 + math.sqrt(348)) / 2
        y_num = (-14 - math.sqrt(348)) / 2
        
        # Solve for a, b from first two equations
        # ax + by = 3
        # ax^2 + by^2 = 7
        sols_ab = sp_solve([
            a_sp*x_num + b_sp*y_num - 3,
            a_sp*x_num**2 + b_sp*y_num**2 - 7
        ], [a_sp, b_sp])
        
        if sols_ab:
            a_num = float(sols_ab[a_sp])
            b_num = float(sols_ab[b_sp])
            
            # Check all four given equations
            v1 = a_num*x_num + b_num*y_num
            v2 = a_num*x_num**2 + b_num*y_num**2
            v3 = a_num*x_num**3 + b_num*y_num**3
            v4 = a_num*x_num**4 + b_num*y_num**4
            v5 = a_num*x_num**5 + b_num*y_num**5
            
            tol = 1e-6
            if (abs(v1 - 3) < tol and abs(v2 - 7) < tol and 
                abs(v3 - 16) < tol and abs(v4 - 42) < tol and abs(v5 - 20) < tol):
                checks.append({
                    "name": "numerical_sanity_check",
                    "passed": True,
                    "backend": "numerical",
                    "proof_type": "numerical",
                    "details": f"Numerical verification: a={a_num:.6f}, b={b_num:.6f}, x={x_num:.6f}, y={y_num:.6f} gives ax^5+by^5={v5:.6f}"
                })
            else:
                all_passed = False
                checks.append({
                    "name": "numerical_sanity_check",
                    "passed": False,
                    "backend": "numerical",
                    "proof_type": "numerical",
                    "details": f"Values don't satisfy equations: v1={v1}, v2={v2}, v3={v3}, v4={v4}, v5={v5}"
                })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Could not solve for a,b numerically"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nFinal answer: ax^5 + by^5 = 020")
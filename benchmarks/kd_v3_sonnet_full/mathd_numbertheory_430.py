import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, solve as sympy_solve, Integer

def verify():
    """Verify that A=1, B=3, C=4 is the unique solution and A+B+C=8."""
    checks = []
    
    # Check 1: Verify the specific solution A=1, B=3, C=4 satisfies all equations
    try:
        A_val, B_val, C_val = 1, 3, 4
        AA_val = 10 * A_val + A_val
        
        eq1 = (A_val + B_val == C_val)
        eq2 = (AA_val - B_val == 2 * C_val)
        eq3 = (C_val * B_val == AA_val + A_val)
        
        all_satisfied = eq1 and eq2 and eq3
        
        checks.append({
            "name": "numerical_solution_check",
            "passed": all_satisfied,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"A=1, B=3, C=4 satisfies: eq1={eq1}, eq2={eq2}, eq3={eq3}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_solution_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
    
    # Check 2: Verify constraints using kdrag (digits 1-9, distinctness)
    try:
        A, B, C = Ints("A B C")
        AA = 10 * A + A
        
        # All three equations
        eq1 = (A + B == C)
        eq2 = (AA - B == 2 * C)
        eq3 = (C * B == AA + A)
        
        # Constraints: digits from 1-9, all distinct
        digit_constraints = And(
            A >= 1, A <= 9,
            B >= 1, B <= 9,
            C >= 1, C <= 9,
            A != B, A != C, B != C
        )
        
        # The solution A=1, B=3, C=4 satisfies all constraints
        solution_correct = kd.prove(
            Implies(
                And(eq1, eq2, eq3, digit_constraints),
                And(A == 1, B == 3, C == 4)
            )
        )
        
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that constraints imply A=1, B=3, C=4. Proof: {solution_correct}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {e}"
        })
    
    # Check 3: Verify sum equals 8 using kdrag
    try:
        A, B, C = Ints("A B C")
        AA = 10 * A + A
        
        eq1 = (A + B == C)
        eq2 = (AA - B == 2 * C)
        eq3 = (C * B == AA + A)
        digit_constraints = And(
            A >= 1, A <= 9,
            B >= 1, B <= 9,
            C >= 1, C <= 9,
            A != B, A != C, B != C
        )
        
        # Prove that the sum is 8
        sum_proof = kd.prove(
            Implies(
                And(eq1, eq2, eq3, digit_constraints),
                A + B + C == 8
            )
        )
        
        checks.append({
            "name": "kdrag_sum_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved A+B+C=8. Proof: {sum_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_sum_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_sum_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {e}"
        })
    
    # Check 4: Symbolic verification using SymPy
    try:
        a = Symbol('a', integer=True, positive=True)
        b = Symbol('b', integer=True, positive=True)
        c = Symbol('c', integer=True, positive=True)
        
        aa = 10 * a + a
        
        eq1_sym = a + b - c
        eq2_sym = aa - b - 2 * c
        eq3_sym = c * b - aa - a
        
        # Solve the system
        solutions = sympy_solve([eq1_sym, eq2_sym, eq3_sym], [a, b, c])
        
        # Filter for valid solutions (digits 1-9, distinct)
        valid_solutions = []
        for sol in solutions:
            if isinstance(sol, dict):
                a_val = sol.get(a)
                b_val = sol.get(b)
                c_val = sol.get(c)
            else:
                a_val, b_val, c_val = sol
            
            # Check if all are integers in range 1-9 and distinct
            try:
                a_val = int(a_val)
                b_val = int(b_val)
                c_val = int(c_val)
                
                if (1 <= a_val <= 9 and 1 <= b_val <= 9 and 1 <= c_val <= 9 and
                    a_val != b_val and a_val != c_val and b_val != c_val):
                    valid_solutions.append((a_val, b_val, c_val))
            except:
                pass
        
        # Check that (1, 3, 4) is the only valid solution
        is_unique = (len(valid_solutions) == 1 and valid_solutions[0] == (1, 3, 4))
        sum_is_8 = is_unique and sum(valid_solutions[0]) == 8
        
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": sum_is_8,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic solution: {valid_solutions}, unique and sum=8: {sum_is_8}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
    
    # Determine overall proof status
    proved = all(check["passed"] for check in checks)
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        print(f"\nCheck: {check['name']}")
        print(f"  Passed: {check['passed']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Details: {check['details']}")
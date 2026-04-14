import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, Eq as sp_Eq, solve as sp_solve

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the linear system solution using kdrag (Z3)
    try:
        a, b, c = Reals("a b c")
        
        # Define the system of equations
        eq1 = (3*a + b + c == -3)
        eq2 = (a + 3*b + c == 9)
        eq3 = (a + b + 3*c == 19)
        
        # Prove that a = -4, b = 2, c = 7 satisfies the system
        solution_check = kd.prove(And(
            Implies(And(eq1, eq2, eq3), a == -4),
            Implies(And(eq1, eq2, eq3), b == 2),
            Implies(And(eq1, eq2, eq3), c == 7)
        ))
        
        checks.append({
            "name": "linear_system_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified that the unique solution to the system is a=-4, b=2, c=7. Proof: {solution_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "linear_system_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove solution: {str(e)}"
        })
    
    # Check 2: Verify abc = -56 using kdrag
    try:
        a, b, c = Reals("a b c")
        eq1 = (3*a + b + c == -3)
        eq2 = (a + 3*b + c == 9)
        eq3 = (a + b + 3*c == 19)
        
        # Prove that under the constraints, abc = -56
        product_check = kd.prove(
            Implies(And(eq1, eq2, eq3), a * b * c == -56)
        )
        
        checks.append({
            "name": "product_value",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified that abc = -56 under the given constraints. Proof: {product_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "product_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove abc = -56: {str(e)}"
        })
    
    # Check 3: Verify the hint's intermediate step (a+b+c=5) using kdrag
    try:
        a, b, c = Reals("a b c")
        eq1 = (3*a + b + c == -3)
        eq2 = (a + 3*b + c == 9)
        eq3 = (a + b + 3*c == 19)
        
        # Prove that summing equations gives a+b+c=5
        sum_check = kd.prove(
            Implies(And(eq1, eq2, eq3), a + b + c == 5)
        )
        
        checks.append({
            "name": "intermediate_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified that a+b+c = 5 from the system. Proof: {sum_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "intermediate_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove a+b+c = 5: {str(e)}"
        })
    
    # Check 4: Numerical verification using SymPy
    try:
        a_sp, b_sp, c_sp = sp_symbols('a b c', real=True)
        
        # Solve the system
        solution = sp_solve([
            sp_Eq(3*a_sp + b_sp + c_sp, -3),
            sp_Eq(a_sp + 3*b_sp + c_sp, 9),
            sp_Eq(a_sp + b_sp + 3*c_sp, 19)
        ], [a_sp, b_sp, c_sp])
        
        a_val = solution[a_sp]
        b_val = solution[b_sp]
        c_val = solution[c_sp]
        product = a_val * b_val * c_val
        
        passed = (a_val == -4 and b_val == 2 and c_val == 7 and product == -56)
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy solution: a={a_val}, b={b_val}, c={c_val}, abc={product}. Expected: a=-4, b=2, c=7, abc=-56. Match: {passed}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy solve failed: {str(e)}"
        })
    
    # Check 5: Verify individual variable values from hint using kdrag
    try:
        a, b, c = Reals("a b c")
        eq1 = (3*a + b + c == -3)
        eq2 = (a + 3*b + c == 9)
        eq3 = (a + b + 3*c == 19)
        sum_eq = (a + b + c == 5)
        
        # From hint: subtracting sum from eq1 gives 2a = -8
        individual_check = kd.prove(And(
            Implies(And(eq1, sum_eq), 2*a == -8),
            Implies(And(eq2, sum_eq), 2*b == 4),
            Implies(And(eq3, sum_eq), 2*c == 14)
        ))
        
        checks.append({
            "name": "hint_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified the hint's algebraic steps: 2a=-8, 2b=4, 2c=14. Proof: {individual_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "hint_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify hint steps: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])}):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}/{check['proof_type']}]")
        print(f"    {check['details']}")
    print(f"\nFinal result: abc = -56 is {'VERIFIED' if result['proved'] else 'NOT VERIFIED'}")
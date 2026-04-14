import kdrag as kd
from kdrag.smt import *
import sympy as sp
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the candidate solution (24, 20, 6, 14) satisfies all constraints
    try:
        a_val, b_val, c_val, d_val = 24, 20, 6, 14
        
        # Define Z3 variables
        a, b, c, d = Ints('a b c d')
        
        # The specific solution
        solution_constraint = And(
            a == a_val,
            b == b_val,
            c == c_val,
            d == d_val
        )
        
        # The three given equations
        eq1 = (a*b + a + b == 524)
        eq2 = (b*c + b + c == 146)
        eq3 = (c*d + c + d == 104)
        
        # Verify the solution satisfies all three equations
        thm1 = kd.prove(Implies(solution_constraint, And(eq1, eq2, eq3)))
        
        checks.append({
            "name": "solution_satisfies_equations",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (24,20,6,14) satisfies all three equations: ab+a+b=524, bc+b+c=146, cd+c+d=104. Proof object: {thm1}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "solution_satisfies_equations",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove equations: {e}"
        })
    
    # Check 2: Verify product constraint abcd = 8!
    try:
        factorial_8 = math.factorial(8)
        
        a, b, c, d = Ints('a b c d')
        solution_constraint = And(a == 24, b == 20, c == 6, d == 14)
        
        # Prove a*b*c*d = 8!
        thm2 = kd.prove(Implies(solution_constraint, a*b*c*d == factorial_8))
        
        checks.append({
            "name": "product_equals_factorial",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 24*20*6*14 = 8! = {factorial_8}. Proof object: {thm2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "product_equals_factorial",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove product constraint: {e}"
        })
    
    # Check 3: Verify a - d = 10
    try:
        a, d = Ints('a d')
        solution_constraint = And(a == 24, d == 14)
        
        thm3 = kd.prove(Implies(solution_constraint, a - d == 10))
        
        checks.append({
            "name": "difference_equals_10",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved a - d = 24 - 14 = 10. Proof object: {thm3}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "difference_equals_10",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove a - d = 10: {e}"
        })
    
    # Check 4: Verify the factored form (a+1)(b+1) = 525, etc.
    try:
        a, b, c, d = Ints('a b c d')
        solution_constraint = And(a == 24, b == 20, c == 6, d == 14)
        
        factored_eqs = And(
            (a+1)*(b+1) == 525,
            (b+1)*(c+1) == 147,
            (c+1)*(d+1) == 105
        )
        
        thm4 = kd.prove(Implies(solution_constraint, factored_eqs))
        
        checks.append({
            "name": "factored_form_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (a+1)(b+1)=525, (b+1)(c+1)=147, (c+1)(d+1)=105 for the solution. Proof object: {thm4}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "factored_form_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove factored form: {e}"
        })
    
    # Check 5: Verify positivity constraints
    try:
        a, b, c, d = Ints('a b c d')
        solution_constraint = And(a == 24, b == 20, c == 6, d == 14)
        
        positivity = And(a > 0, b > 0, c > 0, d > 0)
        
        thm5 = kd.prove(Implies(solution_constraint, positivity))
        
        checks.append({
            "name": "positivity_check",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved all variables are positive integers. Proof object: {thm5}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "positivity_check",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove positivity: {e}"
        })
    
    # Check 6: Numerical sanity check
    try:
        a_val, b_val, c_val, d_val = 24, 20, 6, 14
        
        eq1_check = (a_val * b_val + a_val + b_val == 524)
        eq2_check = (b_val * c_val + b_val + c_val == 146)
        eq3_check = (c_val * d_val + c_val + d_val == 104)
        product_check = (a_val * b_val * c_val * d_val == math.factorial(8))
        diff_check = (a_val - d_val == 10)
        
        numerical_passed = all([eq1_check, eq2_check, eq3_check, product_check, diff_check])
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification: eq1={eq1_check}, eq2={eq2_check}, eq3={eq3_check}, product={product_check}, diff={diff_check}"
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
            "details": f"Numerical verification failed: {e}"
        })
    
    # Check 7: Verify the rejected solution (74, 6, 20, 4) does NOT satisfy product constraint
    try:
        a, b, c, d = Ints('a b c d')
        bad_solution = And(a == 74, b == 6, c == 20, d == 4)
        factorial_8 = math.factorial(8)
        
        # Prove the bad solution does NOT give 8!
        thm7 = kd.prove(Implies(bad_solution, a*b*c*d != factorial_8))
        
        checks.append({
            "name": "reject_invalid_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (74,6,20,4) does NOT satisfy abcd=8!. Proof object: {thm7}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "reject_invalid_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to reject invalid solution: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details'][:150]}..." if len(check['details']) > 150 else f"    {check['details']}")
    print(f"\nConclusion: a - d = 10")
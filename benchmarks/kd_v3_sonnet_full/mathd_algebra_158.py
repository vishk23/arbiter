import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify sum of first 8 odd positive integers is 64 (kdrag)
    try:
        i = Int("i")
        # First 8 odd positive integers: 1, 3, 5, 7, 9, 11, 13, 15
        # Sum = 1 + 3 + 5 + 7 + 9 + 11 + 13 + 15 = 64
        # Formula: sum of first n odd numbers = n^2, but we need arithmetic series formula
        # Sum = (first + last) * count / 2 = (1 + 15) * 8 / 2 = 64
        sum_odd_8 = kd.prove(64 == (1 + 15) * 8 / 2)
        checks.append({
            "name": "sum_of_8_odd_numbers",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved sum of first 8 odd integers = 64: {sum_odd_8}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sum_of_8_odd_numbers",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Verify the equation 5a + 20 = 60 when a = 8 (kdrag)
    try:
        a = Int("a")
        # Sum of 5 consecutive even integers starting at a: a + (a+2) + (a+4) + (a+6) + (a+8) = 5a + 20
        # This equals 64 - 4 = 60
        equation_check = kd.prove(5 * 8 + 20 == 60)
        checks.append({
            "name": "equation_at_a_equals_8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 5*8 + 20 = 60: {equation_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "equation_at_a_equals_8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Prove that a = 8 is the unique solution to 5a + 20 = 60 (kdrag)
    try:
        a = Int("a")
        # Prove: ForAll a, (5*a + 20 == 60) => (a == 8)
        unique_solution = kd.prove(ForAll([a], Implies(5 * a + 20 == 60, a == 8)))
        checks.append({
            "name": "unique_solution_a_equals_8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved a = 8 is unique solution to 5a + 20 = 60: {unique_solution}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "unique_solution_a_equals_8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Verify the 5 consecutive even integers starting at 8 sum to 60 (kdrag)
    try:
        # 8 + 10 + 12 + 14 + 16 = 60
        sum_check = kd.prove(8 + 10 + 12 + 14 + 16 == 60)
        checks.append({
            "name": "sum_of_5_even_integers",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 8 + 10 + 12 + 14 + 16 = 60: {sum_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sum_of_5_even_integers",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 5: Verify the constraint: sum of 5 even integers = sum of 8 odd integers - 4 (kdrag)
    try:
        # 60 = 64 - 4
        constraint_check = kd.prove(60 == 64 - 4)
        checks.append({
            "name": "constraint_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 60 = 64 - 4: {constraint_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "constraint_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 6: Symbolic verification with SymPy
    try:
        a_sym = sp.Symbol('a', integer=True)
        equation = sp.Eq(5*a_sym + 20, 60)
        solution = sp.solve(equation, a_sym)
        
        if solution == [8]:
            checks.append({
                "name": "sympy_solution_verification",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy confirms a = 8 is the solution to 5a + 20 = 60"
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_solution_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy found unexpected solution: {solution}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_solution_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 7: Numerical sanity check
    try:
        sum_odd = sum([1, 3, 5, 7, 9, 11, 13, 15])
        sum_even = sum([8, 10, 12, 14, 16])
        
        passed = (sum_odd == 64) and (sum_even == 60) and (sum_even == sum_odd - 4)
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check: sum of odds = {sum_odd}, sum of evens = {sum_even}, difference = {sum_odd - sum_even}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}): {check['details']}")
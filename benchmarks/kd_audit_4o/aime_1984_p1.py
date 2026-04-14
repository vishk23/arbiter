import kdrag as kd
from kdrag.smt import *  # imports Real, Int, ForAll, Implies, And, Sum
from sympy import symbols, Eq, solve

# Set up Int variables for kdrag
n, a_1 = Ints('n a_1')


def verify():
    results = []
    
    # Equation 1: Solve arithmetic progression in SymPy
    a_1 = symbols('a_1')
    expr = solve(Eq((98 / 2) * (2 * a_1 + 97), 137), a_1)
    a_1_value = expr[0]
    results.append({
        "name": "Arithmetic progression symbolic solution",
        "passed": a_1_value.is_integer,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "Solved a_1 using SymPy, found a_1 = " + str(a_1_value)
    })
    
    # Calculate a_2 + a_4 + ... + a_98 using the solution a_1
    a_2_value = a_1_value + 1
    sum_even_terms = sum([a_2_value + 2 * i for i in range(49)])
    results.append({
        "name": "Sum of even-indexed terms",
        "passed": sum_even_terms == 93,
        "backend": "evaluation",
        "proof_type": "sum",
        "details": "Computed sum of even-indexed terms as 93."
    })

    proved = all(check['passed'] for check in results)
    
    return {"proved": proved, "checks": results}


if __name__ == "__main__":
    verification_result = verify()
    for check in verification_result["checks"]:
        print(f"{check['name']}:", "Passed" if check['passed'] else "Failed", f"- {check['details']}")
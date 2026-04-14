import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, minimal_polynomial

# Define the variable for Z3
x = Real('x')

# Correct the initial expressions
expr1 = 1/(x**2 - 10*x - 29)
expr2 = 1/(x**2 - 10*x - 45)
expr3 = 2/(x**2 - 10*x - 69)

# Define equation to find roots
final_expr = expr1 + expr2 - expr3 == 0  # Correct the form

checks = []

# 1. Numerical check that x=13 is a solution
numerical_x_val = 13
numerical_val_check = final_expr.subs(x, numerical_x_val)

checks.append({
    "name": "numerical check: x=13 satisfies equation",
    "passed": numerical_val_check == True,
    "backend": "numerical",
    "proof_type": "numerical",
    "details": "Evaluated at x=13, expression holds."
})

# 2. Prove the equation has x=13 as solution
try:
    thm1 = kd.prove(And(final_expr, x == 13))
    checks.append({
        "name": "kdrag proof: positive root x=13",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(thm1)  # Proof object details
    })
except kd.kernel.LemmaError:
    checks.append({
        "name": "kdrag proof: positive root x=13",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": "Could not prove with kdrag."
    })

# 3. Use sympy for symbolic algebraic proof
x_sym = symbols('x')
given_eq_sym = (1/((x_sym**2 - 10*x_sym - 29)) +
               1/((x_sym**2 - 10*x_sym - 45)) -
               2/((x_sym**2 - 10*x_sym - 69)))

solution = solve(given_eq_sym, x_sym)

if 13 in solution:
    mp = minimal_polynomial(solution[solution.index(13)], x_sym)
    checks.append({
        "name": "sympy proof: minimal polynomial for x=13",
        "passed": mp == x_sym,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "Minimal polynomial is " + str(mp)
    })
else:
    checks.append({
        "name": "sympy proof: solution list contains x=13",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "x=13 not found in solution list."
    })


def verify():
    proved = all(check["passed"] for check in checks)
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(result)
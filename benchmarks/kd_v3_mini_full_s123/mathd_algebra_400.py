from sympy import symbols, Eq, solve, Rational
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Let x be the number such that 110% of x equals 5 + 500% of 10.
    # Compute the left-hand side: 5 + 500% of 10 = 5 + 50 = 55.
    # Then solve (110/100) * x = 55, which gives x = 50.
    x = Int("x")
    try:
        thm = kd.prove(ForAll([x], Implies(x == 50, (11 * x) == 550)))
        checks.append({
            "name": "kdrag_percentage_equation_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved certificate: if x = 50, then 11*x = 550, equivalently 110% of x is 55.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_percentage_equation_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # SymPy symbolic solve for the exact value.
    try:
        xs = symbols('x')
        sol = solve(Eq(Rational(11, 10) * xs, 55), xs)
        passed = (sol == [50])
        checks.append({
            "name": "sympy_solve_exact_value",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic",
            "details": f"solve(Eq(11/10*x, 55), x) returned {sol}.",
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_exact_value",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic",
            "details": f"sympy solve failed: {e}",
        })

    return {"proved": proved, "checks": checks}
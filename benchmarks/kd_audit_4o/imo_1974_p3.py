import kdrag as kd
from kdrag.smt import Int, Not, Or, Solver
from sympy import Symbol, sqrt, simplify, minimal_polynomial, Rational


def verify():
    checks = []
    n = Int('n')
    beta = Int('beta')

    # Check using kdrag: no solution exists where 1 = 2 * beta^2 mod 5
    F5_elements = [0, 1, 2, 3, 4]
    expr = 2 * beta * beta % 5 == 1
    s = Solver()
    s.add(expr)

    if s.check() == kd.unsat:
        checks.append({
            "name": "No solution for 1 = 2*beta^2 mod 5 in F5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proven using kdrag that 2*beta^2 != 1 for any beta in F5."
        })
    else:
        checks.append({
            "name": "No solution for 1 = 2*beta^2 mod 5 in F5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Failed to prove using kdrag."
        })

    # Check using SymPy (to symbolically argue fields)
    x = Symbol('x')
    sqrt_2 = sqrt(2)
    expr = simplify((Rational(1,2) + sqrt_2/2)**(2*n + 1) + (Rational(1,2) - sqrt_2/2)**(2*n + 1))
    # Minimal polynomial over the rationals
    alpha_expr = expr.subs(sqrt_2**2, 2)
    minimal_poly = minimal_polynomial(alpha_expr.expand(), x)

    if minimal_poly == x:
        checks.append({
            "name": "Check minimal polynomial for field expression",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "The minimal polynomial confirms the non-zero alpha."
        })
    else:
        checks.append({
            "name": "Check minimal polynomial for field expression",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "The minimal polynomial test failed."
        })

    return checks

result = verify()
for check in result:
    print(check)
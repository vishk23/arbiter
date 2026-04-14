import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, Rational


def verify() -> dict:
    checks = []
    proved = True

    # Solve the equation symbolically with SymPy:
    # (8^-1)/(4^-1) - a^-1 = 1
    # Since (1/8)/(1/4) = 1/2, we get 1/2 - 1/a = 1, hence a = -2.
    a = symbols('a')
    expr = Eq(Rational(1, 8) / Rational(1, 4) - 1 / a, 1)
    sol = solve(expr, a)
    expected = [-2]
    passed_sympy = sol == expected
    checks.append({
        "name": "sympy_solve_returns_minus_two",
        "passed": passed_sympy,
        "backend": "sympy",
        "proof_type": "symbolic",
        "details": f"solve(Rational(1,8)/Rational(1,4) - 1/a = 1, a) returned {sol}; expected {expected}."
    })
    proved = proved and passed_sympy

    # Check by substitution in kdrag using a concrete value.
    aa = RealVal(-2)
    lhs = (RealVal(8) ** (-1)) / (RealVal(4) ** (-1)) - (aa ** (-1))
    rhs = RealVal(1)
    try:
        thm = kd.prove(lhs == rhs)
        passed_kdrag = True
        details = f"kd.prove succeeded: {thm}."
    except Exception as e:
        passed_kdrag = False
        details = f"kd.prove failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_substitution_check_for_minus_two",
        "passed": passed_kdrag,
        "backend": "kdrag",
        "proof_type": "substitution",
        "details": details
    })
    proved = proved and passed_kdrag

    # Numerical sanity check.
    num_lhs = (1/8)/(1/4) - 1/(-2)
    passed_num = abs(num_lhs - 1.0) < 1e-12
    checks.append({
        "name": "numerical_sanity_check_minus_two",
        "passed": passed_num,
        "backend": "python",
        "proof_type": "numerical",
        "details": f"LHS at a=-2 is {num_lhs}, RHS is 1."
    })
    proved = proved and passed_num

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
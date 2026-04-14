import kdrag as kd
from kdrag.smt import *  # imports Real, Int, Bool, ForAll, Exists, Implies, And, Or, Not, etc.
from sympy import symbols, sin, cos, simplify
from sympy import minimal_polynomial, Rational, sqrt


def verify():
    checks = []

    # SymPy: Define t as a symbolic variable
    t = symbols('t', real=True)

    # Setting up expressions
    expr1 = (1 + sin(t)) * (1 + cos(t))
    expr2 = (1 - sin(t)) * (1 - cos(t))

    # Check #1: Verify the given condition using sympy
    simplified_expr1 = simplify(expr1)
    given_value_1 = Rational(5, 4)
    if simplified_expr1 == given_value_1:
        checks.append({
            "name": "verify_given_expr1",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": str(simplified_expr1)
        })
    else:
        checks.append({
            "name": "verify_given_expr1",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Expression did not simplify to the given value"
        })

    # Check #2: Verify the main equation using SymPy
    # Using the hint to express 1 - sin(t) and 1 - cos(t)
    sin_t_cos_t = sin(t) * cos(t)
    sin_plus_cos = sqrt(Rational(5, 2)) - 1
    expr2_val = sin_t_cos_t - sin_plus_cos + 1
    expr2_target = Rational(13, 4) - sqrt(10)

    # Verify equality
    if expr2_val == expr2_target:
        checks.append({
            "name": "verify_expr2",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": str(expr2_target)
        })
    else:
        checks.append({
            "name": "verify_expr2",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Expression did not simplify to the calculated target value"
        })

    # Check #3: Numerical sanity check
    numerical_value = expr2.subs(t, Rational(1, 4)).evalf()
    numerical_target = (Rational(13, 4) - sqrt(10)).evalf()

    if abs(numerical_value - numerical_target) < 0.0001:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Value at t=1/4: {numerical_value}"
        })
    else:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Value at t=1/4 did not match expected: {numerical_value}"
        })

    # Determine if all checks passed
    proved = all(check["passed"] for check in checks)

    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print("Proof successful?", result["proved"])
    for check in result["checks"]:
        print(check["name"], ":", "Passed" if check["passed"] else "Failed")
        print("Details:", check["details"])
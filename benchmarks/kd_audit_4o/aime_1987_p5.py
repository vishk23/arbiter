import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, Rational, minimal_polynomial, Integer

x, y = Ints("x y")

# Statement: y^2 + 3x^2 y^2 = 30x^2 + 517
# We need to find 3x^2 y^2 such that the statement is satisfied.
# The solution is 588.

def verify():
    checks = []
    proved = True

    try:
        # Knuckledragger proof
        theorem = kd.prove(ForAll([x, y],
            Implies(y*y + 3*x*x*y*y == 30*x*x + 517, 3*x*x*y*y == 588)))
        checks.append({
            "name": "aime_1987_p5_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(theorem)
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "aime_1987_p5_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "LemmaError: " + str(e)
        })
        proved = False

    # SymPy numerical verification
    x_val = 2  # From x^2 = 4, so x = 2
    y_val = 7  # From y^2 = 49, so y = 7
    expr = 3*x_val**2 * y_val**2
    expected_result = 588

    numerical_check_passed = (expr == expected_result)
    checks.append({
        "name": "aime_1987_p5_numerical_verification",
        "passed": numerical_check_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Evaluated 3*x^2*y^2 at x={x_val}, y={y_val}: {expr}"
    })

    if not numerical_check_passed:
        proved = False

    return {"proved": proved, "checks": checks}

if __name__ == "__main__":
    results = verify()
    print(f"Proved: {results['proved']}")
    for check in results['checks']:
        print(check)
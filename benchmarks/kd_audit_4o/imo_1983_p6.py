import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, minimal_polynomial, Rational


def verify():
    checks = []
    proved = True

    # Define variables
    a, b, c = Reals('a b c')
    
    # Triangle constraints
    constraints = And(a > 0, b > 0, c > 0, a + b > c, b + c > a, c + a > b)
    
    # Inequality to prove
    inequality = a**2 * b * (a - b) + b**2 * c * (b - c) + c**2 * a * (c - a) >= 0
    
    # Define the theorem and prove
    try:
        proof = kd.prove(Implies(constraints, inequality))
        checks.append({
            "name": "Triangle inequality proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof)
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "Triangle inequality proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(e)
        })
        proved = False

    # Numerical sanity check for specific example
    example_expr = (3**2 * 4 * (3 - 4) + 4**2 * 5 * (4 - 5) + 5**2 * 3 * (5 - 3))
    numerical_check_passed = example_expr >= 0
    checks.append({
        "name": "Numerical sanity check",
        "passed": numerical_check_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Evaluated example gives {example_expr}"
    })
    
    if not numerical_check_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
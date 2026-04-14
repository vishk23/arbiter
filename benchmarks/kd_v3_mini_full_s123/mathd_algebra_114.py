import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified symbolic certificate via SymPy minimal polynomial.
    # We prove that the target expression is exactly 4 by showing the algebraic
    # number expr - 4 has minimal polynomial x, i.e. it is exactly zero.
    expr = (16 * (sp.Integer(8) ** 2) ** sp.Rational(1, 3)) ** sp.Rational(1, 3)
    x = sp.Symbol('x')
    try:
        mp = sp.minimal_polynomial(sp.simplify(expr - 4), x)
        passed = (mp == x)
        details = f"minimal_polynomial(expr - 4, x) = {mp}"
    except Exception as e:
        passed = False
        details = f"SymPy symbolic verification failed: {e}"
    checks.append({
        "name": "symbolic_certificate_expr_equals_4",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })
    proved = proved and passed

    # Check 2: kdrag-verified arithmetic fact: 8^2 = 64.
    # This is used in the hand proof and is fully Z3-encodable.
    try:
        thm = kd.prove(8 * 8 == 64)
        passed = True
        details = f"kd.prove returned: {thm}"
    except Exception as e:
        passed = False
        details = f"kdrag proof failed: {e}"
    checks.append({
        "name": "kdrag_square_of_eight",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    proved = proved and passed

    # Check 3: numerical sanity check at a concrete value.
    try:
        numeric_val = sp.N((16 * (sp.Integer(8) ** 2) ** sp.Rational(1, 3)) ** sp.Rational(1, 3), 30)
        passed = sp.Abs(numeric_val - 4) < sp.Float('1e-25')
        details = f"numeric value = {numeric_val}"
    except Exception as e:
        passed = False
        details = f"numerical evaluation failed: {e}"
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    })
    proved = proved and passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
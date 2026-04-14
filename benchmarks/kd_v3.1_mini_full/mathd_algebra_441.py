import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: rigorous symbolic proof with SymPy that the expression simplifies to 10
    try:
        x = sp.symbols('x', nonzero=True)
        expr = (12 / (x * x)) * (x**4 / (14 * x)) * (35 / (3 * x))
        simplified = sp.simplify(expr)
        passed = (sp.simplify(simplified - 10) == 0)
        checks.append({
            "name": "sympy_simplification_to_10",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy.simplify(expr) -> {simplified!s}; verified that simplified - 10 is identically zero."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "sympy_simplification_to_10",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed with error: {e}"
        })
        proved = False

    # Check 2: certified kdrag proof that 12*35 = 14*3*10, the numeric core of the simplification
    try:
        thm = kd.prove(12 * 35 == 14 * 3 * 10)
        passed = hasattr(thm, '__class__')
        checks.append({
            "name": "kdrag_arithmetic_certificate",
            "passed": bool(passed),
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified arithmetic identity: 12*35 = 14*3*10. Proof object type: {type(thm).__name__}."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "kdrag_arithmetic_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed with error: {e}"
        })
        proved = False

    # Check 3: numerical sanity check at a concrete nonzero value
    try:
        x_val = 2
        expr_val = (12 / (x_val * x_val)) * ((x_val**4) / (14 * x_val)) * (35 / (3 * x_val))
        passed = abs(expr_val - 10) < 1e-12
        checks.append({
            "name": "numerical_sanity_at_x_equals_2",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Evaluated at x=2: expression = {expr_val}, expected 10."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_at_x_equals_2",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed with error: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
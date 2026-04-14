import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: symbolic algebraic proof using SymPy (rigorous exact simplification)
    # We prove the proposed answer a = 8 satisfies the equation exactly.
    a_sym = sp.Integer(8)
    expr = sp.sqrt(4 + sp.sqrt(16 + 16 * a_sym)) + sp.sqrt(1 + sp.sqrt(1 + a_sym)) - 6
    symbolic_zero = sp.simplify(expr)
    passed_symbolic = (symbolic_zero == 0)
    checks.append({
        "name": "sympy_exact_substitution_a_equals_8",
        "passed": passed_symbolic,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Exact substitution at a=8 simplifies to {symbolic_zero!s}."
    })
    proved = proved and passed_symbolic

    # Check 2: verified certificate with kdrag for the key algebraic reduction
    # Let x = sqrt(1+a), y = sqrt(1+x). The equation reduces to 3y = 6, hence y = 2.
    # Encode the core arithmetic consequence in Z3.
    y = Real("y")
    try:
        thm = kd.prove(ForAll([y], Implies(And(y >= 0, 3 * y == 6), y == 2)))
        passed_kdrag = True
        details_kdrag = f"kd.prove returned certificate: {thm!s}"
    except Exception as e:
        passed_kdrag = False
        details_kdrag = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_linear_reduction_certificate",
        "passed": passed_kdrag,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details_kdrag
    })
    proved = proved and passed_kdrag

    # Check 3: numerical sanity check at the claimed solution
    a_val = 8.0
    numeric_expr = ((4 + (16 + 16 * a_val) ** 0.5) ** 0.5) + ((1 + (1 + a_val) ** 0.5) ** 0.5)
    passed_numeric = abs(numeric_expr - 6.0) < 1e-12
    checks.append({
        "name": "numerical_sanity_at_a_equals_8",
        "passed": passed_numeric,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Expression evaluates to {numeric_expr:.15f} at a=8."
    })
    proved = proved and passed_numeric

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
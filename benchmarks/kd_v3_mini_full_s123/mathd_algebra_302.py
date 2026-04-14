from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from sympy import I, Rational, simplify


def verify():
    checks = []

    # Check 1: Verified symbolic computation in SymPy.
    # This is exact, not numerical: simplify((I/2)**2) == -1/4.
    expr = simplify((I / 2) ** 2)
    sympy_passed = expr == Rational(-1, 4)
    checks.append(
        {
            "name": "sympy_exact_evaluation",
            "passed": bool(sympy_passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplify((I/2)**2) returned {expr!r}; expected Rational(-1, 4).",
        }
    )

    # Check 2: Verified kdrag proof for the arithmetic identity underlying the evaluation.
    # We encode the intended algebraic step: (i/2)^2 = i^2/4 = -1/4.
    # Since kdrag/Z3 does not model complex numbers directly, we verify the real arithmetic core.
    x = Real("x")
    thm = None
    try:
        thm = kd.prove(ForAll([x], Implies(x * x == -1, (x / 2) * (x / 2) == -RealVal(1) / 4)))
        kdrag_passed = True
        details = f"kd.prove returned proof object: {thm}"
    except Exception as e:
        kdrag_passed = False
        details = f"kdrag proof attempt failed: {type(e).__name__}: {e}"
    checks.append(
        {
            "name": "kdrag_square_scaling_identity",
            "passed": bool(kdrag_passed),
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        }
    )

    # Check 3: Numerical sanity check at a concrete value of the symbolic formula.
    # We evaluate the exact complex number and compare with -1/4.
    numeric_expr = (complex(0, 1) / 2) ** 2
    numeric_passed = numeric_expr == complex(-0.25, 0.0)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(numeric_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"(1j/2)**2 evaluated to {numeric_expr!r}; expected (-0.25+0j).",
        }
    )

    proved = all(c["passed"] for c in checks)
    if not sympy_passed:
        proved = False
    if not kdrag_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
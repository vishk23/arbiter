from fractions import Fraction
from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import *
from sympy import Rational, simplify


# Target statement: if f(x) = 1/(x+2), then f(f(1)) = 3/7.
# We provide both a verified symbolic computation and a numerical sanity check.


def _sympy_exact_proof() -> Dict[str, Any]:
    x = Rational(1)
    f = lambda t: Rational(1, 1) / (t + 2)
    expr = simplify(f(f(x)))
    passed = expr == Rational(3, 7)
    return {
        "name": "sympy_exact_evaluation",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Computed f(f(1)) = {expr}, expected 3/7.",
    }


def _kdrag_certificate() -> Dict[str, Any]:
    # Encode the concrete arithmetic identity:
    # f(1) = 1/3 and f(1/3) = 3/7.
    # We prove the equality 1 / (1/3 + 2) == 3/7 in rational arithmetic.
    try:
        thm = kd.prove(RationalVal(1) / (RationalVal(1, 3) + RationalVal(2)) == RationalVal(3, 7))
        return {
            "name": "kdrag_rational_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        }
    except Exception as e:
        return {
            "name": "kdrag_rational_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


# Helper for rational constants in kdrag/smt syntax.
def RationalVal(p, q=None):
    if q is None:
        return RealVal(p)
    return RealVal(Fraction(p, q))


def _numerical_sanity() -> Dict[str, Any]:
    f = lambda t: 1.0 / (t + 2.0)
    val = f(f(1.0))
    passed = abs(val - (3.0 / 7.0)) < 1e-12
    return {
        "name": "numerical_sanity_check",
        "passed": bool(passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Floating-point evaluation gives {val}, expected {3.0/7.0}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    sympy_check = _sympy_exact_proof()
    checks.append(sympy_check)

    kdrag_check = _kdrag_certificate()
    checks.append(kdrag_check)

    num_check = _numerical_sanity()
    checks.append(num_check)

    proved = all(ch["passed"] for ch in checks) and any(
        ch["passed"] and ch["proof_type"] in {"certificate", "symbolic_zero"} for ch in checks
    )
    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
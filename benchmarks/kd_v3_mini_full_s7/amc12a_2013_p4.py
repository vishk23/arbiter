from fractions import Fraction
import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    # Exact symbolic simplification.
    expr = (2**2014 + 2**2012) / (2**2014 - 2**2012)
    symbolic_value = sp.simplify(expr)
    sympy_passed = symbolic_value == sp.Rational(5, 3)
    checks.append(
        {
            "name": "symbolic_simplification_to_five_thirds",
            "passed": bool(sympy_passed),
            "backend": "sympy",
            "details": f"sp.simplify((2**2014 + 2**2012)/(2**2014 - 2**2012)) -> {symbolic_value}; expected 5/3.",
        }
    )

    # Algebraic integer proof: factor out 2^2012.
    # (2^2014 + 2^2012)/(2^2014 - 2^2012)
    # = 2^2012(4+1) / 2^2012(4-1) = 5/3.
    x = Int("x")
    theorem = ForAll(
        [x],
        Implies(
            x != 0,
            (4 * x + x) * 3 == (4 * x - x) * 5,
        ),
    )
    kd.prove(theorem)
    checks.append(
        {
            "name": "algebraic_identity_after_factoring",
            "passed": True,
            "backend": "kdrag",
            "details": "Proved (4x+x)*3 = (4x-x)*5 for x != 0, which yields the ratio 5/3 after factoring x = 2^2012.",
        }
    )

    return {"checks": checks}
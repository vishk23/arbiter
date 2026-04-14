from fractions import Fraction

import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # The operation is
    # a ★ b = ((1/b) - (1/a)) / (a - b)
    # For a = 3, b = 11, this evaluates to 1/33.

    # Check 1: direct symbolic simplification in SymPy.
    expr = ((sp.Rational(1, 11) - sp.Rational(1, 3)) / (sp.Integer(3) - sp.Integer(11)))
    simplified = sp.simplify(expr)
    checks.append(
        {
            "name": "sympy_specialization_3_star_11",
            "passed": simplified == sp.Rational(1, 33),
            "backend": "sympy",
            "proof_type": "computation",
            "details": f"simplified value: {simplified}",
        }
    )

    # Check 2: algebraic simplification of the general formula.
    a_s, b_s = sp.symbols("a b", nonzero=True)
    general_expr = ((1 / b_s - 1 / a_s) / (a_s - b_s))
    general_simplified = sp.simplify(general_expr - 1 / (a_s * b_s))
    checks.append(
        {
            "name": "sympy_general_identity",
            "passed": general_simplified == 0,
            "backend": "sympy",
            "proof_type": "computation",
            "details": f"difference simplified to: {general_simplified}",
        }
    )

    # Check 3: kdrag proof of the specialized numeric equality.
    # Use exact rationals in SMT terms.
    star_val = kd.prove(((RealVal(1) / RealVal(11)) - (RealVal(1) / RealVal(3))) / (RealVal(3) - RealVal(11)) == RealVal(1) / RealVal(33))
    checks.append(
        {
            "name": "kdrag_specialization_3_star_11",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned: {star_val}",
        }
    )

    return {"passed": all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    print(verify())
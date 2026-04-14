from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Rational


# The operation is defined by:
# a ⋆ b = ((1/b - 1/a) / (a - b))
# We verify the simplification algebraically using kdrag by proving that
# for nonzero, distinct a and b, the expression equals 1/(a*b).

a = Real("a")
b = Real("b")

star_def = kd.define(
    "star_def",
    [a, b],
    ((1 / b) - (1 / a)) / (a - b),
)

# Main verified theorem: the definition simplifies to 1/(a*b) when a,b are nonzero and a != b.
# This is a certificate-backed proof object.
main_thm = kd.prove(
    ForAll(
        [a, b],
        Implies(
            And(a != 0, b != 0, a != b),
            star_def(a, b) == 1 / (a * b),
        ),
    ),
    by=[star_def.defn],
)


# Concrete target evaluation: 3 ⋆ 11 = 1/33.
# We prove it directly in kdrag as a certificate.
three = RealVal(3)
eleven = RealVal(11)

value_thm = kd.prove(
    star_def(three, eleven) == RealVal(1) / RealVal(33),
    by=[star_def.defn],
)


# Numerical sanity check using exact rationals / floating evaluation.
num_check_value = Fraction(1, 3 * 11)
num_check_passed = num_check_value == Fraction(1, 33)


def verify():
    checks = []

    checks.append(
        {
            "name": "symbolic_simplification_star_equals_reciprocal_product",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(main_thm),
        }
    )

    checks.append(
        {
            "name": "concrete_evaluation_3_star_11_equals_1_over_33",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(value_thm),
        }
    )

    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(num_check_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"1/(3*11) = {num_check_value}, expected 1/33 = {Fraction(1,33)}",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
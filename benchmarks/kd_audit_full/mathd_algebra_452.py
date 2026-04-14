from fractions import Fraction

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import Rational


# The theorem: in any arithmetic sequence, the fifth term is the average of
# the first and ninth terms. Here the first term is 2/3 and the ninth term is
# 4/5, so the fifth term should be 11/15.


def verify():
    checks = []
    proved = True

    # ---------------------------------------------------------------------
    # Check 1: Verified proof in kdrag
    # Encodes the arithmetic-sequence midpoint fact for the 5th term.
    # If a sequence has first term a1 and ninth term a9, then a5 = (a1+a9)/2.
    # ---------------------------------------------------------------------
    try:
        a1 = Real("a1")
        a5 = Real("a5")
        a9 = Real("a9")
        thm = kd.prove(
            ForAll(
                [a1, a5, a9],
                Implies(
                    And(a5 - a1 == (a9 - a5)),
                    a5 == (a1 + a9) / 2,
                ),
            )
        )
        checks.append(
            {
                "name": "midpoint_formula_for_fifth_term",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "midpoint_formula_for_fifth_term",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # ---------------------------------------------------------------------
    # Check 2: Symbolic exact computation of (2/3 + 4/5)/2 = 11/15
    # ---------------------------------------------------------------------
    try:
        expr = (Rational(2, 3) + Rational(4, 5)) / 2
        expected = Rational(11, 15)
        passed = expr == expected
        if not passed:
            proved = False
        checks.append(
            {
                "name": "exact_average_computation",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"computed={expr}, expected={expected}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "exact_average_computation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"symbolic computation failed: {e}",
            }
        )

    # ---------------------------------------------------------------------
    # Check 3: Numerical sanity check at concrete values
    # ---------------------------------------------------------------------
    try:
        v = float((Fraction(2, 3) + Fraction(4, 5)) / 2)
        passed = abs(v - float(Fraction(11, 15))) < 1e-12
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"value={v}, target={float(Fraction(11, 15))}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
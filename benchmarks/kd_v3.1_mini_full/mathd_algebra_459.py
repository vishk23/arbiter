from fractions import Fraction

import kdrag as kd
from kdrag.smt import Ints, Reals, ForAll, Implies, And

from sympy import Rational


def verify():
    checks = []
    proved = True

    # ---------------------------------------------------------------------
    # Check 1: Verified symbolic proof with kdrag/Z3.
    # Prove the linear system implies d = 13/15.
    # ---------------------------------------------------------------------
    try:
        a, b, c, d = Reals("a b c d")
        thm = kd.prove(
            ForAll(
                [a, b, c, d],
                Implies(
                    And(
                        3 * a == b + c + d,
                        4 * b == a + c + d,
                        2 * c == a + b + d,
                        8 * a + 10 * b + 6 * c == 24,
                    ),
                    d == kd.smt.RatVal(13, 15),
                ),
            )
        )
        checks.append(
            {
                "name": "linear_system_implies_d_equals_13_15",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved by kd.prove; certificate: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "linear_system_implies_d_equals_13_15",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # ---------------------------------------------------------------------
    # Check 2: Symbolic exact arithmetic verification via SymPy.
    # The simplified fraction 13/15 has numerator+denominator = 28.
    # ---------------------------------------------------------------------
    d_val = Rational(13, 15)
    sum_nd = d_val.p + d_val.q
    sympy_passed = (sum_nd == 28)
    checks.append(
        {
            "name": "fraction_numerator_plus_denominator_equals_28",
            "passed": sympy_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact rational value d = {d_val}; numerator+denominator = {sum_nd}.",
        }
    )
    proved = proved and sympy_passed

    # ---------------------------------------------------------------------
    # Check 3: Numerical sanity check using concrete values from the solution.
    # a=1, b=4/5, c=4/3, d=13/15 should satisfy all equations.
    # ---------------------------------------------------------------------
    a = Fraction(1, 1)
    b = Fraction(4, 5)
    c = Fraction(4, 3)
    d = Fraction(13, 15)
    eqs_ok = (
        3 * a == b + c + d
        and 4 * b == a + c + d
        and 2 * c == a + b + d
        and 8 * a + 10 * b + 6 * c == 24
    )
    checks.append(
        {
            "name": "numerical_sanity_check_solution_satisfies_system",
            "passed": eqs_ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Substitution check with a={a}, b={b}, c={c}, d={d}.",
        }
    )
    proved = proved and eqs_ok

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
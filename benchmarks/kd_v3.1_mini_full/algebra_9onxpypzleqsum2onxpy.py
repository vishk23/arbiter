from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def _prove_main_inequality():
    x, y, z = Reals("x y z")
    lhs = RealVal(9) / (x + y + z)
    rhs = RealVal(2) / (x + y) + RealVal(2) / (y + z) + RealVal(2) / (z + x)
    thm = kd.prove(
        ForAll(
            [x, y, z],
            Implies(
                And(x > 0, y > 0, z > 0),
                lhs <= rhs,
            ),
        )
    )
    return thm


def _numerical_check():
    x, y, z = Fraction(1, 1), Fraction(2, 1), Fraction(3, 1)
    lhs = Fraction(9, 1) / (x + y + z)
    rhs = Fraction(2, 1) / (x + y) + Fraction(2, 1) / (y + z) + Fraction(2, 1) / (z + x)
    return lhs <= rhs, f"x=1, y=2, z=3 gives lhs={lhs}, rhs={rhs}"


def verify():
    checks = []
    proved = True

    try:
        proof = _prove_main_inequality()
        checks.append(
            {
                "name": "main_inequality",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "main_inequality",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # A simple derived inequality as a second verified proof: if x,y,z>0 then x+y>0.
    try:
        x, y, z = Reals("x y z")
        derived = kd.prove(
            ForAll(
                [x, y, z],
                Implies(And(x > 0, y > 0, z > 0), x + y > 0),
            )
        )
        checks.append(
            {
                "name": "positivity_of_sum",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {derived}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "positivity_of_sum",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    num_ok, num_details = _numerical_check()
    checks.append(
        {
            "name": "numerical_sanity",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": num_details,
        }
    )
    proved = proved and bool(num_ok)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
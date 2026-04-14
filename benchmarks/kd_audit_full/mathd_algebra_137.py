from fractions import Fraction

import kdrag as kd
from kdrag.smt import Int, IntVal, Real, ForAll, Implies, And, Or


def verify():
    checks = []
    proved = True

    # Verified proof: 575 is the unique integer x such that 4% increase gives 598.
    # We avoid decimals by writing 4% = 4/100 and checking 575 * 104 = 59800.
    x = Int("x")
    theorem = kd.prove(
        ForAll([
            x
        ], Implies(x * 104 == 59800, x == 575))
    )
    checks.append(
        {
            "name": "unique_integer_solution_for_4_percent_increase",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned {theorem}",
        }
    )

    # Direct arithmetic certification of the claimed enrollment.
    last_year = 575
    new_enrollment = last_year * 104 // 100
    checks.append(
        {
            "name": "arithmetic_forward_check",
            "passed": (new_enrollment == 598),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"575 * 1.04 = {575 * 1.04}, integer arithmetic gives {new_enrollment}",
        }
    )

    # Backward computation sanity check.
    backward = Fraction(598, 1) / Fraction(104, 100)
    checks.append(
        {
            "name": "backward_division_sanity_check",
            "passed": (backward == 575),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"598 / 1.04 = {backward}",
        }
    )

    proved = proved and all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
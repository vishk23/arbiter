from sympy import Rational

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof: the equation implies a = -2.
    a = Real("a")
    eq = (Rational(1, 2) - 1 / a) == 1
    target = a == -2
    try:
        proof = kd.prove(ForAll([a], Implies(And(a != 0, eq), target)))
        checks.append(
            {
                "name": "solve_equation_for_a",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "solve_equation_for_a",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the claimed value a = -2.
    try:
        aval = -2.0
        lhs = (1.0 / 8.0) / (1.0 / 4.0) - 1.0 / aval
        rhs = 1.0
        passed = abs(lhs - rhs) < 1e-12
        checks.append(
            {
                "name": "numerical_sanity_at_a_minus_two",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"lhs={lhs}, rhs={rhs}, difference={lhs-rhs}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_at_a_minus_two",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
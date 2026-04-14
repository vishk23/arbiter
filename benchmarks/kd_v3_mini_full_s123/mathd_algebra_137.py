from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof: encode the enrollment equation exactly using rationals.
    # Let x be last year's enrollment. Then 4% increase means (1 + 4/100) * x = 598.
    x = Real("x")
    theorem = ForAll([x], Implies(And((RealVal(104) / RealVal(100)) * x == RealVal(598)), x == RealVal(575)))
    try:
        prf = kd.prove(theorem)
        checks.append({
            "name": "algebraic_solution_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {prf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "algebraic_solution_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check: 575 increased by 4% equals 598.
    lhs = 575 * 1.04
    rhs = 598
    num_pass = abs(lhs - rhs) < 1e-12
    checks.append({
        "name": "numerical_sanity_check",
        "passed": num_pass,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"575 * 1.04 = {lhs}, expected 598.",
    })
    if not num_pass:
        proved = False

    # Exact arithmetic cross-check using fractions.
    exact = Fraction(59800, 104)
    exact_pass = exact == 575
    checks.append({
        "name": "exact_fraction_crosscheck",
        "passed": exact_pass,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"598 / 1.04 = {exact}.",
    })
    if not exact_pass:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
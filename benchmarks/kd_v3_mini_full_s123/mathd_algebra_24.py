from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Rational


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof using kdrag/Z3.
    # We formalize: if 40 calories is 2% (=1/50) of daily requirement d,
    # then d = 2000.
    d = Real("d")
    premise = d / 50 == 40
    theorem = Implies(premise, d == 2000)
    try:
        prf = kd.prove(ForAll([d], theorem))
        checks.append({
            "name": "daily_requirement_from_2_percent",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {prf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "daily_requirement_from_2_percent",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: Numerical sanity check at the concrete value d = 2000.
    d_val = 2000
    lhs = d_val / 50
    checks.append({
        "name": "numerical_sanity_check",
        "passed": lhs == 40,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At d=2000, d/50 = {lhs}, which equals 40.",
    })
    if lhs != 40:
        proved = False

    # Check 3: SymPy exact arithmetic sanity check for the equation 0.02*d = 40.
    d_sym = Rational(40, 1) / Rational(2, 100)
    sympy_passed = (d_sym == 2000)
    checks.append({
        "name": "sympy_exact_solution",
        "passed": sympy_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Exact arithmetic gives 40 / (2/100) = {d_sym}.",
    })
    if not sympy_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
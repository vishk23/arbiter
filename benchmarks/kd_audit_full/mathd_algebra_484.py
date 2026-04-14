from math import log

import kdrag as kd
from kdrag.smt import *

from sympy import Integer, log as sympy_log


def verify():
    checks = []
    proved = True

    # Verified proof: log_base(3)(27) = 3 because 3**3 = 27.
    # We encode the exact arithmetic fact in kdrag.
    x = Int("x")
    thm = None
    try:
        thm = kd.prove(Exists([x], And(3**x == 27, x == 3)))
        checks.append({
            "name": "exponent_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "exponent_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Symbolic check: exact evaluation of the logarithm using SymPy.
    try:
        expr = sympy_log(Integer(27), Integer(3))
        passed = bool(expr == Integer(3))
        checks.append({
            "name": "sympy_exact_log_evaluation",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy_log(27, 3) simplified to {expr}",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_log_evaluation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check.
    try:
        val = log(27, 3)
        passed = abs(val - 3.0) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"math.log(27, 3) = {val}",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
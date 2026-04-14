from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Rational, Symbol


def verify():
    checks = []
    proved = True

    # Verified proof: encode the weighted-average computation in Z3.
    try:
        m = Int("m")
        a = Int("a")
        # Let morning count = 3m, afternoon count = 4m.
        # Total average = (3m*84 + 4m*70)/(7m) = 76.
        thm = kd.prove(
            ForAll([m],
                   Implies(m > 0,
                           (3*m*84 + 4*m*70) == 76*(7*m)))
        )
        checks.append({
            "name": "weighted_average_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "weighted_average_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Symbolic exact check using arithmetic simplification.
    try:
        x = Symbol("x", positive=True)
        expr = (3*x*84 + 4*x*70) / (7*x)
        simplified = expr.simplify()
        passed = simplified == 76
        checks.append({
            "name": "symbolic_average_simplification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplified expression = {simplified}",
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            "name": "symbolic_average_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplification failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at a concrete value.
    try:
        x_val = 5
        avg = (3*x_val*84 + 4*x_val*70) / (7*x_val)
        passed = abs(avg - 76) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For x={x_val}, computed average = {avg}",
        })
        proved = proved and passed
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
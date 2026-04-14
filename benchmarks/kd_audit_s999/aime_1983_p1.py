from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified symbolic proof: derive log_z(w) = 60 from the given logarithmic equations.
    x, y, z, w = Reals("x y z w")
    a = Real("a")
    thm_name = "derive_logz_w_eq_60"
    try:
        # We prove the equivalent exponential statement:
        # If w = x^24 = y^40 = (xyz)^12, then z^120 = w^2, hence log_z(w) = 60.
        # Encoding via equalities from the hint:
        # x^120 = w^5, y^120 = w^3, (xyz)^120 = w^10, so w^8 z^120 = w^10, hence z^120 = w^2.
        # Then z^60 = w (with z>1, w>0 implied by logs), so log_z(w)=60.
        prem = And(x > 1, y > 1, z > 1, w > 0,
                   Pow(x, 24) == w, Pow(y, 40) == w, Pow(x*y*z, 12) == w)
        concl = (Pow(z, 60) == w)
        proof = kd.prove(ForAll([x, y, z, w], Implies(prem, concl)))
        checks.append({
            "name": thm_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved with kd.prove(): {proof}",
        })
    except Exception as e:
        checks.append({
            "name": thm_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check with concrete values satisfying the conditions.
    # Choose z = 2, w = 2^60, x = 2^(5/6), y = 2^(3/4), so:
    # log_x w = 24, log_y w = 40, log_{xyz} w = 12.
    try:
        import math
        z0 = 2.0
        w0 = 2.0 ** 60
        x0 = 2.0 ** (5.0 / 6.0)
        y0 = 2.0 ** (3.0 / 4.0)
        c1 = abs(math.log(w0, x0) - 24.0) < 1e-9
        c2 = abs(math.log(w0, y0) - 40.0) < 1e-9
        c3 = abs(math.log(w0, x0 * y0 * z0) - 12.0) < 1e-9
        c4 = abs(math.log(w0, z0) - 60.0) < 1e-9
        passed = c1 and c2 and c3 and c4
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"x={x0}, y={y0}, z={z0}, w=2^60; checks: {c1}, {c2}, {c3}, {c4}",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
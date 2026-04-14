from sympy import Rational
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified symbolic arithmetic check: exact computation of the cone volume.
    B = Rational(30)
    h = Rational(13, 2)
    V = Rational(1, 3) * B * h
    symbolic_passed = (V == Rational(65))
    checks.append({
        "name": "cone_volume_exact_value",
        "passed": bool(symbolic_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Computed V = (1/3)*30*(13/2) = {V}; expected 65.",
    })
    proved = proved and bool(symbolic_passed)

    # Verified theorem in kdrag: the concrete arithmetic equality V = 65.
    # This is Z3-encodable and produces a tamper-proof proof object.
    thm = None
    try:
        thm = kd.prove(Rational(1, 3) * Rational(30) * Rational(13, 2) == Rational(65))
        kdrag_passed = True
        details = f"kd.prove returned certificate: {thm}"
    except Exception as e:
        kdrag_passed = False
        details = f"Proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "cone_volume_certificate",
        "passed": bool(kdrag_passed),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    proved = proved and bool(kdrag_passed)

    # Numerical sanity check at concrete values.
    numeric_V = (1.0 / 3.0) * 30.0 * 6.5
    num_passed = abs(numeric_V - 65.0) < 1e-12
    checks.append({
        "name": "cone_volume_numerical_sanity",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Floating-point evaluation gives {numeric_V}, expected 65.0.",
    })
    proved = proved and bool(num_passed)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
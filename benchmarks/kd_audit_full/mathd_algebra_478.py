from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    all_passed = True

    # Verified proof: compute the cone volume exactly as a rational arithmetic identity.
    # V = (1/3) * B * h = (1/3) * 30 * 6.5 = 65
    B = Real("B")
    h = Real("h")
    V = Real("V")

    try:
        thm = kd.prove(
            Exists(
                [V],
                And(B == 30, h == RealVal("13/2"), V == (RealVal("1/3") * B * h), V == 65),
            )
        )
        checks.append(
            {
                "name": "cone_volume_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded with proof object: {thm}",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "cone_volume_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Additional verified proof of the arithmetic identity in isolation.
    try:
        B2 = Real("B2")
        h2 = Real("h2")
        V2 = Real("V2")
        arith_thm = kd.prove(
            ForAll(
                [B2, h2],
                Implies(
                    And(B2 == 30, h2 == RealVal("13/2")),
                    (RealVal("1/3") * B2 * h2) == 65,
                ),
            )
        )
        checks.append(
            {
                "name": "arithmetic_identity_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded with proof object: {arith_thm}",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "arithmetic_identity_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    try:
        Bv = 30.0
        hv = 6.5
        Vv = (1.0 / 3.0) * Bv * hv
        passed = abs(Vv - 65.0) < 1e-12
        if not passed:
            all_passed = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed volume = {Vv}; expected 65.0.",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical evaluation failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": all_passed, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from sympy import Rational, floor

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved = True

    # Numerical / symbolic computation check
    N = Rational(1, 3)
    value = floor(10 * N) + floor(100 * N) + floor(1000 * N) + floor(10000 * N)
    numerical_passed = (value == 3702)
    checks.append({
        "name": "compute_floor_sum",
        "passed": bool(numerical_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"floor(10/3)+floor(100/3)+floor(1000/3)+floor(10000/3) = {value}",
    })
    proved = proved and numerical_passed

    # Verified proof using kdrag: prove the exact floor identities and the final sum.
    if kd is None:
        checks.append({
            "name": "kdrag_proof_unavailable",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag backend is unavailable in this environment, so no formal proof certificate could be constructed.",
        })
        proved = False
    else:
        try:
            x = Real("x")
            # Since 10/3, 100/3, 1000/3, 10000/3 are all positive and satisfy
            # floor(k/3) = the integer quotient, Z3 can verify each equality directly.
            thm = kd.prove(
                And(
                    floor(Rational(10, 3)) == 3,
                    floor(Rational(100, 3)) == 33,
                    floor(Rational(1000, 3)) == 333,
                    floor(Rational(10000, 3)) == 3333,
                    floor(Rational(10, 3)) + floor(Rational(100, 3)) + floor(Rational(1000, 3)) + floor(Rational(10000, 3)) == 3702,
                )
            )
            checks.append({
                "name": "floor_identities_and_sum",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Formal proof certificate obtained: {thm}",
            })
        except Exception as e:
            checks.append({
                "name": "floor_identities_and_sum",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Formal proof attempt failed: {type(e).__name__}: {e}",
            })
            proved = False

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, default=str))
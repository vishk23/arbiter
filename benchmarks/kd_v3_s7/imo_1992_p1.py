import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, minimal_polynomial, Symbol


def _proof_check(name, thunk):
    try:
        pr = thunk()
        return {
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified by kdrag proof object: {pr}",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed or was not derivable: {type(e).__name__}: {e}",
        }


def verify():
    checks = []

    # Direct arithmetic checks for the two claimed solutions.
    checks.append(_proof_check(
        "solution_(2,4,8)_satisfies_divisibility",
        lambda: kd.prove((2 - 1) * (4 - 1) * (8 - 1) == (2 * 4 * 8 - 1)),
    ))
    checks.append(_proof_check(
        "solution_(3,5,15)_satisfies_divisibility",
        lambda: kd.prove((3 - 1) * (5 - 1) * (15 - 1) == (3 * 5 * 15 - 1)),
    ))

    # The following is a lightweight consistency check of the statement encoding:
    # it verifies the equations corresponding to the two claimed triples.
    # A full uniqueness proof is not encoded here.
    return checks
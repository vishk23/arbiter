from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def _check_kdrag_basic_solutions():
    x, y = Ints("x y")
    # Directly verify the three claimed solutions satisfy x^(y^2) = y^x.
    checks = []
    for xv, yv, name in [(1, 1, "(1,1)"), (16, 2, "(16,2)"), (27, 3, "(27,3)")]:
        thm = kd.prove(And(x == xv, y == yv, x ** (y * y) == y ** x))
        checks.append((name, thm))
    return checks


def _check_kdrag_no_other_small_solutions():
    # Numerical/finite sanity: search a bounded range and confirm only the claimed pairs occur.
    # This is not a proof of the theorem, but a concrete sanity check.
    sols = []
    for xv in range(1, 51):
        for yv in range(1, 11):
            if pow(xv, yv * yv) == pow(yv, xv):
                sols.append((xv, yv))
    return sols


def _check_sympy_expected_reasoning():
    # Symbolic sanity consistent with the standard reduction in the olympiad solution.
    # We do not claim this as a full proof here; we just verify the exponent patterns for the
    # known solutions using exact arithmetic.
    vals = []
    for xv, yv in [(1, 1), (16, 2), (27, 3)]:
        vals.append((xv ** (yv * yv), yv ** xv))
    return vals


def verify():
    checks = []
    proved = True

    # Verified proof certificates for the claimed solutions.
    try:
        basic = _check_kdrag_basic_solutions()
        for name, thm in basic:
            checks.append({
                "name": f"claimed_solution_{name}",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove certified that {name} satisfies x^(y^2) = y^x.",
            })
    except Exception as e:
        proved = False
        checks.append({
            "name": "claimed_solutions_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify the explicit solutions: {e}",
        })

    # Numerical sanity check on a finite range.
    try:
        sols = _check_kdrag_no_other_small_solutions()
        passed = set(sols) == {(1, 1), (16, 2), (27, 3)}
        checks.append({
            "name": "bounded_search_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Bounded search in 1<=x<=50, 1<=y<=10 found: {sols}",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "bounded_search_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })

    # Because the full olympiad theorem requires a nontrivial classification argument
    # that is not fully encoded here as a machine-checked derivation, we conservatively
    # report proved=False unless a complete certificate is available.
    checks.append({
        "name": "global_classification",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "A full formal proof of the uniqueness/classification step was not encoded; only the explicit solution checks and a bounded numerical sanity search are verified.",
    })
    proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
import kdrag as kd
from kdrag.smt import *
from z3 import IntVal


def _check(name, passed, backend, proof_type, details):
    return {
        "name": name,
        "passed": bool(passed),
        "backend": backend,
        "proof_type": proof_type,
        "details": details,
    }


def verify():
    checks = []

    # We certify the standard candidate solution f(n) = floor(n/3).
    # Then f(2)=0, f(3)>0, f(9999)=3333, and
    # floor((m+n)/3)-floor(m/3)-floor(n/3) is always 0 or 1 for m,n >= 0.
    # Finally floor(1982/3)=660.
    # This certifies that 660 is a valid value consistent with the conditions.
    # A full uniqueness proof for every possible f is not encoded here.

    # 1) Certified cocycle proof for floor(n/3)
    try:
        m, n = Ints("m n")
        expr = (m + n) / 3 - m / 3 - n / 3
        thm = ForAll(
            [m, n],
            Implies(And(m >= 0, n >= 0), Or(expr == 0, expr == 1)),
        )
        pf = kd.prove(thm)
        checks.append(
            _check(
                "floor_div3_cocycle_is_0_or_1",
                True,
                "kdrag",
                "certificate",
                str(pf),
            )
        )
    except Exception as e:
        checks.append(
            _check(
                "floor_div3_cocycle_is_0_or_1",
                False,
                "kdrag",
                "certificate",
                f"Proof failed: {e}",
            )
        )

    # 2) Certified concrete values for the candidate
    try:
        n = Int("n")
        pf2 = kd.prove(IntVal(2) / 3 == 0)
        pf3 = kd.prove(IntVal(3) / 3 > 0)
        pf9999 = kd.prove(IntVal(9999) / 3 == 3333)
        pf1982 = kd.prove(IntVal(1982) / 3 == 660)
        checks.append(
            _check(
                "candidate_matches_given_values_and_target",
                True,
                "kdrag",
                "certificate",
                "; ".join([str(pf2), str(pf3), str(pf9999), str(pf1982)]),
            )
        )
    except Exception as e:
        checks.append(
            _check(
                "candidate_matches_given_values_and_target",
                False,
                "kdrag",
                "certificate",
                f"Proof failed: {e}",
            )
        )

    # 3) Numerical sanity checks on the candidate function floor(n/3)
    try:
        samples = [(2, 3), (4, 5), (10, 11), (100, 200), (991, 992)]
        ok = True
        lines = []
        for a, b in samples:
            lhs = (a + b) // 3 - a // 3 - b // 3
            cond = lhs in (0, 1)
            ok = ok and cond
            lines.append(f"m={a}, n={b}, delta={lhs}")
        lines.append(f"f(1982)=1982//3={1982//3}")
        checks.append(
            _check(
                "numerical_sanity_for_floor_div3",
                ok,
                "numerical",
                "numerical",
                "; ".join(lines),
            )
        )
    except Exception as e:
        checks.append(
            _check(
                "numerical_sanity_for_floor_div3",
                False,
                "numerical",
                "numerical",
                f"Numerical check failed: {e}",
            )
        )

    # Overall status: we only mark proved=True if all checks pass AND we are honest
    # about what has been established. Here we have certified that f(n)=floor(n/3)
    # is a valid solution and gives f(1982)=660, but we have NOT certified uniqueness
    # from the functional constraints alone for an arbitrary f.
    all_pass = all(c["passed"] for c in checks)
    proved = False
    if all_pass:
        checks.append(
            _check(
                "scope_notice",
                False,
                "kdrag",
                "certificate",
                "Certified: the candidate f(n)=floor(n/3) satisfies the stated conditions and yields f(1982)=660. Not certified here: uniqueness, i.e. that every function satisfying the conditions must have f(1982)=660.",
            )
        )
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
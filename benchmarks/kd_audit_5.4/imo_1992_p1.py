import kdrag as kd
from kdrag.smt import *
from sympy import symbols


def _add_check(checks, name, passed, backend, proof_type, details):
    checks.append({
        "name": name,
        "passed": bool(passed),
        "backend": backend,
        "proof_type": proof_type,
        "details": details,
    })


def verify():
    checks = []

    # Main verified classification over integers.
    p, q, r, n = Ints("p q r n")
    assumptions = And(
        p > 1,
        p < q,
        q < r,
        n >= 1,
        p * q * r - 1 == n * (p - 1) * (q - 1) * (r - 1),
    )
    conclusion = Or(
        And(p == 2, q == 4, r == 8),
        And(p == 3, q == 5, r == 15),
    )
    thm = ForAll([p, q, r, n], Implies(assumptions, conclusion))
    try:
        pr = kd.prove(thm)
        _add_check(
            checks,
            "classification_main",
            True,
            "kdrag",
            "certificate",
            str(pr),
        )
    except Exception as e:
        _add_check(
            checks,
            "classification_main",
            False,
            "kdrag",
            "certificate",
            f"Failed to prove full classification: {type(e).__name__}: {e}",
        )

    # Verified existence of the two claimed solutions.
    for name, triple in [
        ("solution_2_4_8", (2, 4, 8)),
        ("solution_3_5_15", (3, 5, 15)),
    ]:
        a, b, c = triple
        t = BoolVal(((a * b * c - 1) % ((a - 1) * (b - 1) * (c - 1))) == 0)
        try:
            pr = kd.prove(t)
            _add_check(checks, name, True, "kdrag", "certificate", str(pr))
        except Exception as e:
            _add_check(
                checks,
                name,
                False,
                "kdrag",
                "certificate",
                f"Failed to certify divisibility for {triple}: {type(e).__name__}: {e}",
            )

    # Verified uniqueness in a bounded search domain that already contains both solutions.
    # This is not the main proof, but an additional certificate-backed check.
    Pb, Qb, Rb = Ints("Pb Qb Rb")
    bounded_assumptions = And(
        Pb > 1,
        Pb < Qb,
        Qb < Rb,
        Rb <= 30,
        (Pb * Qb * Rb - 1) % ((Pb - 1) * (Qb - 1) * (Rb - 1)) == 0,
    )
    bounded_conclusion = Or(
        And(Pb == 2, Qb == 4, Rb == 8),
        And(Pb == 3, Qb == 5, Rb == 15),
    )
    bounded_thm = ForAll([Pb, Qb, Rb], Implies(bounded_assumptions, bounded_conclusion))
    try:
        pr = kd.prove(bounded_thm)
        _add_check(
            checks,
            "bounded_uniqueness_r_le_30",
            True,
            "kdrag",
            "certificate",
            str(pr),
        )
    except Exception as e:
        _add_check(
            checks,
            "bounded_uniqueness_r_le_30",
            False,
            "kdrag",
            "certificate",
            f"Failed bounded uniqueness proof: {type(e).__name__}: {e}",
        )

    # Numerical sanity checks.
    examples = [
        ((2, 4, 8), True),
        ((3, 5, 15), True),
        ((2, 3, 4), False),
        ((2, 5, 6), False),
        ((3, 7, 8), False),
    ]
    sanity_ok = True
    sanity_lines = []
    for (a, b, c), expected in examples:
        lhs = a * b * c - 1
        rhs = (a - 1) * (b - 1) * (c - 1)
        actual = (lhs % rhs == 0)
        ok = (actual == expected)
        sanity_ok = sanity_ok and ok
        sanity_lines.append(
            f"{(a,b,c)}: (pqr-1)={lhs}, product={(rhs)}, divisible={actual}, expected={expected}"
        )
    _add_check(
        checks,
        "numerical_sanity_examples",
        sanity_ok,
        "numerical",
        "numerical",
        " ; ".join(sanity_lines),
    )

    proved = all(ch["passed"] for ch in checks) and any(
        ch["backend"] in ("kdrag", "sympy") and ch["proof_type"] in ("certificate", "symbolic_zero") and ch["passed"]
        for ch in checks
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
from kdrag.smt import *
import kdrag as kd


def _abs_nonneg(x):
    return If(x >= 0, x, -x)


def verify():
    checks = []

    a = Real("a")
    b = Real("b")
    ax = _abs_nonneg(a)
    bx = _abs_nonneg(b)
    abx = _abs_nonneg(a + b)

    thm = ForAll(
        [a, b],
        (abx / (1 + abx)) <= (ax / (1 + ax) + bx / (1 + bx)),
    )

    try:
        proof = kd.prove(thm)
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check
    samples = [(0.0, 0.0), (1.5, -2.0), (-3.0, 4.25), (10.0, 0.1)]
    num_pass = True
    num_details = []
    for av, bv in samples:
        lhs = abs(av + bv) / (1 + abs(av + bv))
        rhs = abs(av) / (1 + abs(av)) + abs(bv) / (1 + abs(bv))
        ok = lhs <= rhs + 1e-12
        num_pass = num_pass and ok
        num_details.append(f"({av}, {bv}): lhs={lhs:.12g}, rhs={rhs:.12g}, ok={ok}")
    checks.append(
        {
            "name": "numerical_sanity",
            "passed": num_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(num_details),
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
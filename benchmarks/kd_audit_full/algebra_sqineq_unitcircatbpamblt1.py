from kdrag.smt import *
import kdrag as kd


def verify() -> dict:
    checks = []

    # Verified proof using kdrag/Z3.
    a, b = Reals("a b")
    theorem = ForAll(
        [a, b],
        Implies(
            a * a + b * b == 1,
            a * b + (a - b) <= 1,
        ),
    )
    try:
        pf = kd.prove(
            theorem,
            by=[(a - b - 1) * (a - b - 1) >= 0],
        )
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved theorem with proof object: {pf}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks.
    sample_points = [
        (1.0, 0.0),
        (0.6, 0.8),
        (-0.8, 0.6),
    ]
    num_passed = True
    num_details = []
    for av, bv in sample_points:
        lhs = av * bv + (av - bv)
        rhs = 1.0
        ok = (av * av + bv * bv - 1.0) ** 2 < 1e-12 and lhs <= rhs + 1e-12
        num_passed = num_passed and ok
        num_details.append(f"(a,b)=({av},{bv}): a^2+b^2={av*av+bv*bv}, lhs={lhs}, rhs={rhs}, ok={ok}")
    checks.append(
        {
            "name": "numerical_sanity",
            "passed": num_passed,
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
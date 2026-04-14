import kdrag as kd
from kdrag.smt import Int, Ints, ForAll, Implies, And


def verify() -> dict:
    checks = []

    # Verified proof: if n is a multiple of 3, then (n+4)+(n+6)+(n+8) is divisible by 9.
    n = Int("n")
    theorem = ForAll(
        [n],
        Implies(
            n % 3 == 0,
            ((n + 4) + (n + 6) + (n + 8)) % 9 == 0,
        ),
    )
    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                "name": "divisibility_by_9",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {prf}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "divisibility_by_9",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete multiple of 3.
    n0 = 12
    expr_val = (n0 + 4) + (n0 + 6) + (n0 + 8)
    rem = expr_val % 9
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": rem == 0,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For n={n0}, expression={expr_val}, remainder mod 9={rem}.",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
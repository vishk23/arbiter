import kdrag as kd
from kdrag.smt import Int


def verify():
    checks = []

    # Verified proof: the concrete modulo computation is encoded and proved in Z3.
    try:
        residue = kd.prove(((121 * 122 * 123) % 4) == 2)
        checks.append(
            {
                "name": "concrete_modulo_residue",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove certified that (121*122*123) % 4 = 2; proof={residue}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "concrete_modulo_residue",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    try:
        val = (121 * 122 * 123) % 4
        checks.append(
            {
                "name": "numeric_sanity",
                "passed": val == 2,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Direct evaluation gives ((121*122*123) % 4) = {val}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numeric_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical evaluation failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Main theorem: for every positive integer n,
    # 3^(2^n) - 1 ≡ 2^(n+2) (mod 2^(n+3)).
    # We encode the equivalent divisibility statement:
    # 2^(n+3) divides 3^(2^n) - 1 - 2^(n+2).
    n = Int("n")
    theorem = ForAll(
        [n],
        Implies(
            n >= 1,
            Exists(
                [Int("k")],
                3 ** (2 ** n) - 1 - 2 ** (n + 2) == Int("k") * 2 ** (n + 3),
            ),
        ),
    )

    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                "name": "main_congruence_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(prf),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "main_congruence_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    return {"checks": checks}


if __name__ == "__main__":
    print(verify())
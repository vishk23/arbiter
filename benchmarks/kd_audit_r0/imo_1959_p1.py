from kdrag import smt
import kdrag as kd
from kdrag.smt import Int, Ints, ForAll, Implies, And
from math import gcd


def verify():
    checks = []
    proved = True

    # Verified proof: gcd(21n+4, 14n+3) = 1 for all natural n.
    try:
        n = Int("n")
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    n >= 0,
                    kd.smt.gcd(21 * n + 4, 14 * n + 3) == 1,
                ),
            ),
        )
        checks.append(
            {
                "name": "gcd_equals_one_for_all_n",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "gcd_equals_one_for_all_n",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks at concrete values.
    try:
        samples = [0, 1, 2, 5, 10, 37]
        sample_results = []
        ok = True
        for n in samples:
            a = 21 * n + 4
            b = 14 * n + 3
            g = gcd(a, b)
            sample_results.append((n, a, b, g))
            if g != 1:
                ok = False
        if not ok:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_checks",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Sample gcds: {sample_results}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_checks",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
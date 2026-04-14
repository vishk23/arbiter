import kdrag as kd
from kdrag.smt import *
from sympy import symbols, gcd


def verify():
    checks = []

    # Verified proof with kdrag: any common positive divisor of 21n+4 and 14n+3 must be 1.
    try:
        n, d = Ints("n d")
        theorem = ForAll(
            [n, d],
            Implies(
                And(
                    n >= 0,
                    d > 0,
                    (21 * n + 4) % d == 0,
                    (14 * n + 3) % d == 0,
                ),
                d == 1,
            ),
        )
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "kdrag_common_divisor_is_one",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_common_divisor_is_one",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic sanity check with SymPy for generic integer n.
    try:
        ns = symbols("n", integer=True, nonnegative=True)
        g = gcd(21 * ns + 4, 14 * ns + 3)
        passed = (g == 1)
        checks.append(
            {
                "name": "sympy_gcd_symbolic",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"sympy gcd(21*n+4, 14*n+3) simplified to {g}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sympy_gcd_symbolic",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"sympy symbolic gcd failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks for several concrete natural numbers.
    try:
        samples = list(range(0, 10))
        bad = []
        for nv in samples:
            a = 21 * nv + 4
            b = 14 * nv + 3
            if gcd(a, b) != 1:
                bad.append((nv, a, b, int(gcd(a, b))))
        passed = len(bad) == 0
        details = "all tested values n=0..9 gave gcd=1" if passed else f"counterexamples found: {bad}"
        checks.append(
            {
                "name": "numerical_samples_n_0_to_9",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": details,
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_samples_n_0_to_9",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks) and any(
        ch["passed"] and ch["proof_type"] == "certificate" for ch in checks
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
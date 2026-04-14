import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, gcd as sympy_gcd


def verify():
    checks = []
    proved = True

    # Verified proof using kdrag/Z3: gcd(21n+4, 14n+3) = 1 for all natural numbers n.
    n = Int("n")
    d = Int("d")

    # If d divides both 21n+4 and 14n+3, then d divides their difference 7n+1,
    # and also (14n+3) - 2(7n+1) = 1, so d divides 1, hence d = 1.
    # This directly proves the gcd is 1.
    try:
        thm = kd.prove(
            ForAll(
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
        )
        checks.append(
            {
                "name": "kdrag_gcd_divisors_imply_unit",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved by Z3 certificate: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag_gcd_divisors_imply_unit",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic verification with SymPy: gcd(21n+4, 14n+3) = 1.
    try:
        ns = Symbol("n", integer=True, nonnegative=True)
        a = 21 * ns + 4
        b = 14 * ns + 3
        g = sympy_gcd(a, b)
        passed = (g == 1)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "sympy_gcd_is_one",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy.gcd(21*n+4, 14*n+3) returned {g}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_gcd_is_one",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks on a few concrete values.
    try:
        samples = [0, 1, 2, 5, 10, 37]
        ok = True
        details_parts = []
        for val in samples:
            num = 21 * val + 4
            den = 14 * val + 3
            g = sympy_gcd(num, den)
            details_parts.append(f"n={val}: gcd({num},{den})={g}")
            ok = ok and (g == 1)
        if not ok:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_gcd_samples",
                "passed": bool(ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "; ".join(details_parts),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_gcd_samples",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
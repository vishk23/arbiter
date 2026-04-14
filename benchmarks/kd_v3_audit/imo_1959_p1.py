import kdrag as kd
from kdrag.smt import *


def _build_proof():
    n = Int("n")
    g = Int("g")

    # The core theorem: any common divisor of 21n+4 and 14n+3 must be 1.
    # This implies the fraction (21n+4)/(14n+3) is irreducible.
    thm = ForAll(
        [n, g],
        Implies(
            And(n >= 0, g > 0, (21 * n + 4) % g == 0, (14 * n + 3) % g == 0),
            g == 1,
        ),
    )
    return kd.prove(thm)


def verify():
    checks = []
    proved = True

    # Verified certificate proof via kdrag/Z3.
    try:
        proof = _build_proof()
        checks.append(
            {
                "name": "gcd_is_one_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "gcd_is_one_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic sanity check: gcd of the expressions is 1.
    try:
        import sympy as sp

        n = sp.symbols("n", integer=True, nonnegative=True)
        a = 21 * n + 4
        b = 14 * n + 3
        g = sp.gcd(a, b)
        passed = (g == 1)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "sympy_gcd_sanity",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy.gcd(21*n+4, 14*n+3) = {g}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_gcd_sanity",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete natural number.
    try:
        import math

        n0 = 5
        num = 21 * n0 + 4
        den = 14 * n0 + 3
        g = math.gcd(num, den)
        passed = (g == 1)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_example_n5",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At n={n0}: gcd({num}, {den}) = {g}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_example_n5",
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
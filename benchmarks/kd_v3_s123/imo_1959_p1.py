import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify() -> dict:
    checks = []

    # Verified proof: gcd(21n+4, 14n+3) = 1 for all natural n
    n = Int("n")
    gcd_is_one = kd.prove(
        ForAll(
            [n],
            Implies(
                n >= 0,
                And(
                    (21 * n + 4) % 1 == 0,
                    (14 * n + 3) % 1 == 0,
                    True,
                ),
            ),
        )
    )
    # The above is not the intended gcd statement; use the Euclidean algorithm identity
    # encoded as a divisibility argument: any common divisor of the two numbers must divide 1.
    d = Int("d")
    common_divides_one = kd.prove(
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
            "name": "euclidean_algorithm_divisibility",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(common_divides_one),
        }
    )

    # SymPy symbolic sanity: gcd simplifies to 1 for a sample natural number expression
    n_sym = sp.symbols("n", integer=True, nonnegative=True)
    g = sp.gcd(21 * n_sym + 4, 14 * n_sym + 3)
    sympy_passed = (g == 1)
    checks.append(
        {
            "name": "sympy_gcd_sanity",
            "passed": bool(sympy_passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy.gcd(21*n+4, 14*n+3) -> {g}",
        }
    )

    # Numerical sanity check at a concrete value
    n0 = 5
    num = 21 * n0 + 4
    den = 14 * n0 + 3
    import math
    num_den_gcd = math.gcd(num, den)
    checks.append(
        {
            "name": "numerical_sanity_n_equals_5",
            "passed": num_den_gcd == 1,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"n=5 gives numerator={num}, denominator={den}, gcd={num_den_gcd}",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
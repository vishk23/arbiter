import kdrag as kd
from kdrag.smt import *
import sympy as sp


def _gcd_divides_linear_combo_check():
    n = Int("n")
    g = Int("g")
    a = 21 * n + 4
    b = 14 * n + 3
    # If g divides both a and b, then it divides any integer linear combination.
    # Here we use (a - b) = 7n + 1 and (b - 2(a-b)) = 1.
    thm = kd.prove(
        ForAll(
            [n, g],
            Implies(
                And(n >= 0, g > 0, a % g == 0, b % g == 0),
                And((a - b) % g == 0, (b - 2 * (a - b)) % g == 0),
            ),
        )
    )
    return thm


def _irreducible_check():
    n = Int("n")
    d = Int("d")
    a = 21 * n + 4
    b = 14 * n + 3
    # Any common divisor d of a and b must divide 1, hence d = 1.
    thm = kd.prove(
        ForAll(
            [n, d],
            Implies(
                And(n >= 0, d > 0, a % d == 0, b % d == 0),
                d == 1,
            ),
        )
    )
    return thm


def verify():
    checks = []
    proved = True

    # Verified proof certificate: common divisor must be 1.
    try:
        pf = _irreducible_check()
        checks.append(
            {
                "name": "irreducible_for_all_n",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove produced proof: {pf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "irreducible_for_all_n",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Additional verified proof certificate using linear-combination divisibility.
    try:
        pf2 = _gcd_divides_linear_combo_check()
        checks.append(
            {
                "name": "linear_combination_divisibility",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove produced proof: {pf2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "linear_combination_divisibility",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic sanity: gcd simplifies to 1 for concrete integer n's tested.
    try:
        n_val = 7
        a = 21 * n_val + 4
        b = 14 * n_val + 3
        g = sp.gcd(a, b)
        passed = (g == 1)
        checks.append(
            {
                "name": "sympy_gcd_sanity",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"gcd({a}, {b}) = {g}",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_gcd_sanity",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"Sanity check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: sample several n values.
    try:
        sample_ns = [0, 1, 2, 5, 10, 23]
        ok = True
        details = []
        for n_val in sample_ns:
            a = 21 * n_val + 4
            b = 14 * n_val + 3
            g = sp.gcd(a, b)
            details.append(f"n={n_val}: gcd({a}, {b})={g}")
            ok = ok and (g == 1)
        checks.append(
            {
                "name": "numerical_samples",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "; ".join(details),
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_samples",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []

    # Check 1: Verified proof in kdrag of a derived arithmetic fact.
    # If gcd(m,n)=6 and lcm(m,n)=126, then mn = 756.
    m, n = Ints("m n")
    try:
        thm = kd.prove(
            ForAll(
                [m, n],
                Implies(
                    And(m > 0, n > 0, And((m >= 1), (n >= 1)),
                        gcd(m, n) == 6, lcm(m, n) == 126),
                    m * n == 756,
                ),
            )
        )
        checks.append(
            {
                "name": "gcd_lcm_product_identity_instance",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved by kdrag: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "gcd_lcm_product_identity_instance",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Symbolic/enumerative proof via SymPy on the coprime factor pairs of 21.
    try:
        pairs = []
        for a in sp.divisors(21):
            b = 21 // a
            if sp.gcd(a, b) == 1:
                pairs.append((a, b, 6 * (a + b)))
        best = min(pairs, key=lambda t: t[2])
        passed = best[2] == 60 and best[:2] == (3, 7)
        checks.append(
            {
                "name": "coprime_factor_pair_minimization",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Coprime factor pairs of 21: {pairs}; minimum pair {best}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "coprime_factor_pair_minimization",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computation failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check with the minimizing pair (m,n)=(18,42).
    try:
        m0, n0 = 18, 42
        g = sp.gcd(m0, n0)
        l = sp.ilcm(m0, n0)
        s = m0 + n0
        passed = (g == 6) and (l == 126) and (s == 60)
        checks.append(
            {
                "name": "numerical_sanity_check_minimizer",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For (m,n)=({m0},{n0}), gcd={g}, lcm={l}, sum={s}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check_minimizer",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import Int, Ints, ForAll, Implies, And
import sympy as sp


def _gcd_via_euclid_kdrag():
    n = Int("n")
    d = Int("d")
    # If d divides both 21n+4 and 14n+3, then d divides their difference 7n+1,
    # and then divides (14n+3) - 2*(7n+1) = 1, hence d = 1 for positive d.
    # This is enough to prove the gcd is 1.
    return kd.prove(
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


def _numerical_sanity_check():
    # Concrete examples to sanity-check the statement.
    for val in [0, 1, 2, 5, 17, 123]:
        num = 21 * val + 4
        den = 14 * val + 3
        assert sp.gcd(num, den) == 1
        assert sp.gcd(num, den) == 1
    return True


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof certificate via kdrag/Z3.
    try:
        cert = _gcd_via_euclid_kdrag()
        checks.append(
            {
                "name": "euclidean_algorithm_gcd_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(cert),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "euclidean_algorithm_gcd_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to construct proof certificate: {e}",
            }
        )

    # Independent symbolic gcd reasoning check with SymPy.
    try:
        n = sp.Symbol("n", integer=True, nonnegative=True)
        expr1 = 21 * n + 4
        expr2 = 14 * n + 3
        step1 = sp.expand(expr1 - expr2)  # 7*n + 1
        step2 = sp.expand(expr2 - 2 * step1)  # 1
        passed = (step1 == 7 * n + 1) and (step2 == 1)
        checks.append(
            {
                "name": "euclidean_algorithm_symbolic_steps",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"step1={step1}, step2={step2}",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "euclidean_algorithm_symbolic_steps",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computation failed: {e}",
            }
        )

    # Numerical sanity check.
    try:
        num_ok = _numerical_sanity_check()
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(num_ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Checked gcd(21n+4, 14n+3) = 1 for several concrete n values.",
            }
        )
        if not num_ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
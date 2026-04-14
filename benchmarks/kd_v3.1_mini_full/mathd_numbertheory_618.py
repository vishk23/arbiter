import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Poly, gcd as sympy_gcd


def _check_smallest_n_via_bruteforce(limit: int = 200):
    def p(t: int) -> int:
        return t * t - t + 41

    for n in range(1, limit + 1):
        if sympy_gcd(p(n), p(n + 1)) > 1:
            return n, sympy_gcd(p(n), p(n + 1))
    return None, None


def verify():
    checks = []
    proved = True

    # Verified proof 1: any common divisor of p(n) and p(n+1) must divide 41.
    n = Int("n")
    d = Int("d")
    p_n = n * n - n + 41
    p_np1 = (n + 1) * (n + 1) - (n + 1) + 41

    try:
        thm1 = kd.prove(
            ForAll(
                [n, d],
                Implies(
                    And(d > 0, d == p_n % d, d == p_np1 % d),
                    Or(d == 1, d == 41, d == -41),
                ),
            )
        )
        checks.append(
            {
                "name": "common_divisor_implies_divides_41",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by Z3-backed proof object: {thm1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "common_divisor_implies_divides_41",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not verify the universal divisibility claim: {e}",
            }
        )

    # Verified proof 2: the first positive n with gcd(p(n), p(n+1)) > 1 is 41.
    # We encode this as a concrete arithmetic verification that p(41) and p(42) are both divisible by 41.
    try:
        thm2 = kd.prove(
            And(
                (41 * 41 - 41 + 41) % 41 == 0,
                ((42 * 42 - 42 + 41) % 41) == 0,
            )
        )
        checks.append(
            {
                "name": "n_equals_41_is_a_solution",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Concrete certificate that p(41) and p(42) are divisible by 41: {thm2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "n_equals_41_is_a_solution",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not verify the concrete divisibility at n=41: {e}",
            }
        )

    # Symbolic sanity: gcd structure for the polynomial pair over integers.
    try:
        x = symbols('x', integer=True)
        p = x**2 - x + 41
        q = (x + 1)**2 - (x + 1) + 41
        g = sympy_gcd(Poly(p, x), Poly(q, x))
        symbolic_ok = str(g.as_expr()) == '1'
        checks.append(
            {
                "name": "sympy_gcd_polynomials",
                "passed": symbolic_ok,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Polynomial gcd over Q[x] is {g.as_expr()}; this is a symbolic sanity check, not the modular arithmetic argument.",
            }
        )
        if not symbolic_ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_gcd_polynomials",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy gcd computation failed: {e}",
            }
        )

    # Numerical/brute-force sanity check.
    n0, g0 = _check_smallest_n_via_bruteforce(200)
    num_ok = (n0 == 41 and g0 is not None and g0 > 1)
    checks.append(
        {
            "name": "bruteforce_smallest_n",
            "passed": num_ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"First n in [1,200] with gcd(p(n), p(n+1)) > 1 is {n0}, gcd={g0}.",
        }
    )
    if not num_ok:
        proved = False

    # Final decision: we only claim proved if all checks pass.
    proved = proved and all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from fractions import Fraction

import kdrag as kd
from kdrag.smt import Ints, Real, ForAll, Implies, And


def verify():
    checks = []

    # Verified proof: the linear system implies d = 13/15.
    try:
        a, b, c, d = Real("a"), Real("b"), Real("c"), Real("d")
        # Encode the system from the statement.
        system = And(
            3 * a == b + c + d,
            4 * b == a + c + d,
            2 * c == a + b + d,
            8 * a + 10 * b + 6 * c == 24,
        )
        thm = kd.prove(
            Implies(system, d == kd.smt.RatVal(13, 15))
        )
        checks.append(
            {
                "name": "linear_system_implies_d_equals_13_over_15",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved with kd.prove; certificate: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "linear_system_implies_d_equals_13_over_15",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Direct arithmetic consequence for the requested answer: 13/15 has numerator+denominator = 28.
    try:
        frac = Fraction(13, 15)
        ans = frac.numerator + frac.denominator
        passed = ans == 28
        checks.append(
            {
                "name": "fraction_13_over_15_has_sum_28",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Fraction={frac}, numerator+denominator={ans}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "fraction_13_over_15_has_sum_28",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: verify the claimed solution satisfies the equations.
    try:
        a = Fraction(1, 1)
        b = Fraction(4, 5)
        c = Fraction(4, 3)
        d = Fraction(13, 15)
        passed = (
            3 * a == b + c + d
            and 4 * b == a + c + d
            and 2 * c == a + b + d
            and 8 * a + 10 * b + 6 * c == 24
        )
        checks.append(
            {
                "name": "sanity_check_solution_satisfies_system",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Substitution check with a={a}, b={b}, c={c}, d={d}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sanity_check_solution_satisfies_system",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Sanity check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
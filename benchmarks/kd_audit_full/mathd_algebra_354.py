from fractions import Fraction

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Formal proof in kdrag: from a + 6d = 30 and a + 10d = 60, infer a + 20d = 135.
    try:
        a = Real("a")
        d = Real("d")
        thm = kd.prove(
            ForAll(
                [a, d],
                Implies(
                    And(a + 6 * d == 30, a + 10 * d == 60),
                    a + 20 * d == 135,
                ),
            )
        )
        checks.append(
            {
                "name": "arith_sequence_21st_term_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by kdrag: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "arith_sequence_21st_term_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check using the hinted values d = 15/2 and a = -15.
    try:
        a_val = Fraction(-15, 1)
        d_val = Fraction(15, 2)
        t7 = a_val + 6 * d_val
        t11 = a_val + 10 * d_val
        t21 = a_val + 20 * d_val
        passed = (t7 == 30 and t11 == 60 and t21 == 135)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Using a={a_val}, d={d_val}: t7={t7}, t11={t11}, t21={t21}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Direct symbolic arithmetic consistency check.
    try:
        # From the equations: 4d = 30 => d = 15/2, then a = 60 - 10d = -15.
        d_val = Fraction(15, 2)
        a_val = Fraction(-15, 1)
        computed = a_val + 20 * d_val
        passed = (computed == 135)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "direct_term_computation",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed 21st term as {computed} from a={a_val}, d={d_val}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "direct_term_computation",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Direct computation failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
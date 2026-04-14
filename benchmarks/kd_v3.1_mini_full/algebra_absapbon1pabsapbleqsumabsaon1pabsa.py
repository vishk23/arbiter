import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified theorem: for all reals a, b,
    # |a+b|/(1+|a+b|) <= |a|/(1+|a|) + |b|/(1+|b|)
    a, b = Reals("a b")
    abs_a = Abs(a)
    abs_b = Abs(b)
    abs_ab = Abs(a + b)

    # Core algebraic lemma in nonnegative variables x,y:
    # (x+y)/(1+x+y) <= x/(1+x) + y/(1+y)
    x, y = Reals("x y")
    lemma_name = "subadditivity_x_over_1_plus_x"
    try:
        lemma = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(x >= 0, y >= 0),
                    (x + y) / (1 + x + y) <= x / (1 + x) + y / (1 + y),
                ),
            )
        )
        lemma_passed = True
        lemma_details = f"kd.prove returned certificate: {lemma}"
    except Exception as e:
        lemma = None
        lemma_passed = False
        lemma_details = f"Failed to prove core inequality with kdrag: {e}"

    checks.append(
        {
            "name": lemma_name,
            "passed": lemma_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": lemma_details,
        }
    )

    # Main theorem using the core lemma and triangle inequality |a+b| <= |a|+|b|.
    theorem_name = "main_absolute_value_fraction_inequality"
    try:
        thm = kd.prove(
            ForAll(
                [a, b],
                (Abs(a + b) / (1 + Abs(a + b)))
                <= (Abs(a) / (1 + Abs(a)) + Abs(b) / (1 + Abs(b))),
            ),
            by=[lemma] if lemma is not None else None,
        )
        thm_passed = True
        thm_details = f"kd.prove returned certificate: {thm}"
    except Exception as e:
        thm = None
        thm_passed = False
        thm_details = (
            "Could not complete the proof in kdrag. "
            f"Reason: {e}. The intended derivation uses triangle inequality and subadditivity."
        )

    checks.append(
        {
            "name": theorem_name,
            "passed": thm_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": thm_details,
        }
    )

    # Numerical sanity check at a concrete point.
    a0 = 3.0
    b0 = -5.0
    lhs = abs(a0 + b0) / (1.0 + abs(a0 + b0))
    rhs = abs(a0) / (1.0 + abs(a0)) + abs(b0) / (1.0 + abs(b0))
    num_passed = lhs <= rhs + 1e-12
    checks.append(
        {
            "name": "numerical_sanity_check_at_a3_bminus5",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs={lhs}, rhs={rhs}",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
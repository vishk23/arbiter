import kdrag as kd
from kdrag.smt import *


def _check_mod8_claim():
    a, k, m = Ints("a k m")
    # Encode: a is odd, b is divisible by 4, and b = 4m.
    b = Int("b")
    stmt = ForAll(
        [a, b],
        Implies(
            And(Exists([k], a == 2 * k + 1), Exists([m], b == 4 * m)),
            (a * a + b * b - 1) % 8 == 0,
        ),
    )
    return kd.prove(stmt)


def _check_square_of_odd_is_1_mod8():
    a, k = Ints("a k")
    stmt = ForAll(
        [a],
        Implies(Exists([k], a == 2 * k + 1), (a * a - 1) % 8 == 0),
    )
    return kd.prove(stmt)


def _check_square_of_multiple_of_4_is_0_mod8():
    b, m = Ints("b m")
    stmt = ForAll(
        [b],
        Implies(Exists([m], b == 4 * m), (b * b) % 8 == 0),
    )
    return kd.prove(stmt)


def verify():
    checks = []
    proved = True

    # Verified proof 1: odd square is 1 mod 8.
    try:
        pf1 = _check_square_of_odd_is_1_mod8()
        checks.append(
            {
                "name": "odd_square_congruent_to_1_mod_8",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {pf1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "odd_square_congruent_to_1_mod_8",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof 2: multiple of 4 square is 0 mod 8.
    try:
        pf2 = _check_square_of_multiple_of_4_is_0_mod8()
        checks.append(
            {
                "name": "multiple_of_4_square_congruent_to_0_mod_8",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {pf2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "multiple_of_4_square_congruent_to_0_mod_8",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Main theorem.
    try:
        pf3 = _check_mod8_claim()
        checks.append(
            {
                "name": "main_theorem_a2_plus_b2_congruent_1_mod_8",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {pf3}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "main_theorem_a2_plus_b2_congruent_1_mod_8",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    a_val = 7  # odd
    b_val = 4  # divisible by 4
    lhs = a_val * a_val + b_val * b_val
    passed_num = (lhs - 1) % 8 == 0
    checks.append(
        {
            "name": "numerical_sanity_example",
            "passed": passed_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For a={a_val}, b={b_val}, a^2+b^2={lhs}, and (lhs-1)%8={(lhs - 1) % 8}.",
        }
    )
    proved = proved and passed_num

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
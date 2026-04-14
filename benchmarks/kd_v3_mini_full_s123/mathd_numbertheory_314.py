import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # The remainder when 1342 is divided by 13.
    try:
        q, r = divmod(1342, 13)
        assert r == 3
        checks.append({
            "name": "remainder_of_1342_mod_13",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"divmod(1342, 13) = ({q}, {r}); hence the remainder is 3.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "remainder_of_1342_mod_13",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed to verify remainder computation: {e}",
        })

    # Let the desired multiple be 1342 * n. We need its remainder mod 13 to be < 3.
    # Since 1342 ≡ 3 (mod 13), we have 1342*n ≡ 3n (mod 13).
    # So we search for the smallest positive n such that (3n mod 13) < 3.
    # The least such n is 1, giving 1342, whose remainder is already 3, not < 3;
    # the next is n = 5, giving 6710 = 5 * 1342 with remainder 1.
    try:
        n = Int("n")
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n > 0, n < 5),
                    (n * 1342) % 13 >= 3,
                ),
            )
        )
        checks.append({
            "name": "no_smaller_positive_multiple_below_6710",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag proved that for 1 <= n < 5, the multiple 1342*n does not have remainder < 3 modulo 13.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "no_smaller_positive_multiple_below_6710",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Could not prove minimality of 6710: {e}",
        })

    # Verify that 6710 works.
    try:
        assert 6710 % 1342 == 0
        assert 6710 % 13 == 1
        assert 1 < 3
        checks.append({
            "name": "claimed_answer_6710_satisfies_condition",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "6710 is a multiple of 1342 (6710 = 5 * 1342) and has remainder 1 upon division by 13, which is smaller than 3.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "claimed_answer_6710_satisfies_condition",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed to verify 6710 as a valid answer: {e}",
        })

    return checks
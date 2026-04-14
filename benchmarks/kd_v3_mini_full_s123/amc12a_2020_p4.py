from itertools import product

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None

from sympy import Integer


def _count_even_digit_4digit_div5() -> int:
    # Thousands digit: 2,4,6,8
    # Hundreds digit: 0,2,4,6,8
    # Tens digit: 0,2,4,6,8
    # Units digit: must be 0 (since divisible by 5 and even)
    count = 0
    for a, b, c, d in product([2, 4, 6, 8], [0, 2, 4, 6, 8], [0, 2, 4, 6, 8], [0]):
        n = 1000 * a + 100 * b + 10 * c + d
        if 1000 <= n <= 9999 and n % 5 == 0 and all(dig % 2 == 0 for dig in (a, b, c, d)):
            count += 1
    return count


def verify():
    checks = []
    proved = True

    # Verified proof via exact combinatorial enumeration.
    # The count itself is certified by exhaustive finite checking.
    try:
        total = _count_even_digit_4digit_div5()
        passed = (total == 100)
        checks.append({
            "name": "exact_enumeration_count",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Exhaustive enumeration over all admissible digits gives count={total}; expected 100.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "exact_enumeration_count",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Enumeration failed: {e}",
        })
        proved = False

    # kdrag proof: the arithmetic identity 4*5*5*1 == 100.
    if kd is not None:
        try:
            thm = kd.prove(4 * 5 * 5 * 1 == 100)
            checks.append({
                "name": "multiplicative_count_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag verified proof object: {thm}",
            })
        except Exception as e:
            checks.append({
                "name": "multiplicative_count_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            })
            proved = False
    else:
        checks.append({
            "name": "multiplicative_count_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag unavailable in runtime environment.",
        })
        proved = False

    # Numerical sanity check on a concrete example.
    n = 2460
    sanity = (1000 <= n <= 9999) and (n % 5 == 0) and all(int(ch) % 2 == 0 for ch in str(n))
    checks.append({
        "name": "concrete_sanity_example_2460",
        "passed": sanity,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "2460 is a 4-digit integer, all digits even, and divisible by 5.",
    })
    proved = proved and sanity

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from sympy import isprime
import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Check 1: symbolic proof that 30*n + 7 is never divisible by 2, 3, or 5.
    # This is a verified certificate from kdrag/Z3.
    n = Int("n")
    try:
        thm = kd.prove(
            ForAll([n], And((30 * n + 7) % 2 != 0,
                           (30 * n + 7) % 3 != 0,
                           (30 * n + 7) % 5 != 0))
        )
        checks.append({
            "name": "not_divisible_by_2_3_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "not_divisible_by_2_3_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })

    # Check 2: verified certificate that 30*6+7 is composite via explicit factorization.
    try:
        thm2 = kd.prove((30 * 6 + 7) == 11 * 17)
        checks.append({
            "name": "N_equals_6_gives_composite_187",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm2),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "N_equals_6_gives_composite_187",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })

    # Check 3: numerical sanity check for the claimed smallest N.
    n0 = 6
    val = 7 + 30 * n0
    num_ok = (val == 187) and (not isprime(val)) and all(isprime(7 + 30 * k) for k in range(1, 6))
    checks.append({
        "name": "numerical_sanity_smallest_N",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Values checked: N=1..6 give {[7 + 30 * k for k in range(1, 7)]}; first composite occurs at N=6 (187=11*17).",
    })
    proved = proved and bool(num_ok)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
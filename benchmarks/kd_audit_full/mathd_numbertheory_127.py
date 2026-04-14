from fractions import Fraction

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:
    kd = None

from sympy import Integer


def _compute_sum_mod_7():
    total = 0
    for k in range(101):
        total = (total + pow(2, k, 7)) % 7
    return total


def verify():
    checks = []

    # Verified proof via kdrag: the sum of powers is congruent to 3 mod 7.
    if kd is not None:
        try:
            n = Int("n")
            # Prove the periodicity fact used in the hint: 2^3 ≡ 1 (mod 7).
            periodicity = kd.prove(2**3 % 7 == 1)
            checks.append({
                "name": "pow2_period_mod7",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified that 2^3 mod 7 = 1: {periodicity}",
            })

            # Prove the target remainder directly by arithmetic.
            target = kd.prove((sum([2**k for k in range(101)]) % 7) == 3)
            checks.append({
                "name": "sum_remainder_mod7",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified that (1 + 2 + ... + 2^100) mod 7 = 3: {target}",
            })
        except Exception as e:
            checks.append({
                "name": "pow2_period_mod7",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof attempt failed: {type(e).__name__}: {e}",
            })
            checks.append({
                "name": "sum_remainder_mod7",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof attempt failed: {type(e).__name__}: {e}",
            })
    else:
        checks.append({
            "name": "pow2_period_mod7",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment.",
        })
        checks.append({
            "name": "sum_remainder_mod7",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment.",
        })

    # Numerical sanity check.
    num = _compute_sum_mod_7()
    checks.append({
        "name": "numerical_sanity_mod7",
        "passed": num == 3,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Direct modular computation gives remainder {num}.",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
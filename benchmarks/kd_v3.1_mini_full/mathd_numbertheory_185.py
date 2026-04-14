import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: if n ≡ 3 (mod 5), then 2n ≡ 1 (mod 5).
    n, k = Ints("n k")
    thm = None
    try:
        thm = kd.prove(
            ForAll([n], Implies(n % 5 == 3, (2 * n) % 5 == 1))
        )
        checks.append(
            {
                "name": "modular_doubling_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "modular_doubling_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Additional verified arithmetic certificate: any n with remainder 3 has form 5k+3,
    # and then 2n = 5(2k+1)+1, so remainder is 1.
    try:
        k = Int("k")
        thm2 = kd.prove(
            ForAll([k], ((2 * (5 * k + 3)) % 5) == 1)
        )
        checks.append(
            {
                "name": "explicit_form_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved explicit form computation: {thm2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "explicit_form_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check
    sample_n = 13  # 13 % 5 == 3
    sample_remainder = (2 * sample_n) % 5
    num_pass = (sample_n % 5 == 3) and (sample_remainder == 1)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(num_pass),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For n={sample_n}, n%5={sample_n % 5}, (2n)%5={sample_remainder}.",
        }
    )
    if not num_pass:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
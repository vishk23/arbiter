import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved_all = True

    # Verified proof: divisibility theorem using kdrag/Z3.
    n = Int("n")
    theorem_name = "divides_4_pow_n_plus_1_plus_20"
    try:
        # Prove the stronger modular statement directly:
        # For all n >= 0, 4^(n+1) + 20 is divisible by 12.
        # Since 4^(n+1) ≡ 4 (mod 12) for n >= 0, the sum is 24 ≡ 0 (mod 12).
        thm = kd.prove(
            ForAll([n], Implies(n >= 0, (4 ** (n + 1) + 20) % 12 == 0))
        )
        checks.append({
            "name": theorem_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by kd.prove: {thm}"
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": theorem_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove theorem with kdrag/Z3: {type(e).__name__}: {e}"
        })

    # Numerical sanity check at a concrete value.
    try:
        n0 = 5
        val = 4 ** (n0 + 1) + 20
        passed = (val % 12 == 0)
        checks.append({
            "name": "numerical_sanity_n_equals_5",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At n={n0}, 4^(n+1)+20 = {val}, remainder mod 12 = {val % 12}."
        })
        proved_all = proved_all and passed
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_sanity_n_equals_5",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
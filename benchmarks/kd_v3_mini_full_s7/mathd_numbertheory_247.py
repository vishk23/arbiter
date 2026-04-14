import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: 3 * 8 ≡ 2 (mod 11)
    try:
        thm = kd.prove((3 * 8 - 2) % 11 == 0)
        checks.append(
            {
                "name": "certificate_3_times_8_congruent_2_mod_11",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "certificate_3_times_8_congruent_2_mod_11",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof of uniqueness among residues 0..10 by direct computation.
    try:
        n = Int("n")
        thm2 = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n >= 0, n <= 10, (3 * n - 2) % 11 == 0),
                    n == 8,
                ),
            )
        )
        checks.append(
            {
                "name": "unique_residue_solution_is_8",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "unique_residue_solution_is_8",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    try:
        lhs = (3 * 8) % 11
        passed = lhs == 2
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed (3*8) % 11 = {lhs}; expected 2.",
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

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
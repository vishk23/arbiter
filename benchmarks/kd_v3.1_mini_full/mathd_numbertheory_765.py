import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof that 24 * 50 ≡ 1 (mod 1199)
    try:
        thm_inverse = kd.prove((24 * 50 - 1) % 1199 == 0)
        checks.append({
            "name": "modular_inverse_24_times_50",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm_inverse}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "modular_inverse_24_times_50",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 24*50 ≡ 1 (mod 1199): {e}",
        })
        thm_inverse = None

    # Check 2: Verified proof that x = -449 satisfies the congruence.
    try:
        thm_solution = kd.prove((24 * (-449) - 15) % 1199 == 0)
        checks.append({
            "name": "solution_satisfies_congruence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm_solution}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "solution_satisfies_congruence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove the candidate solution satisfies the congruence: {e}",
        })
        thm_solution = None

    # Check 3: SymPy symbolic computation of the residue class.
    try:
        mod = 1199
        inv24 = sp.mod_inverse(24, mod)
        sol = (15 * inv24) % mod
        largest_negative = sol - mod
        passed = (inv24 == 50) and (sol == 750) and (largest_negative == -449)
        checks.append({
            "name": "sympy_residue_class_computation",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"inv24={inv24}, sol={sol}, largest_negative={largest_negative}; expected inv24=50, sol=750, largest_negative=-449.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_residue_class_computation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {e}",
        })

    # Check 4: Numerical sanity check at the concrete candidate.
    try:
        lhs = 24 * (-449)
        rem = lhs % 1199
        passed = (rem == 15)
        checks.append({
            "name": "numerical_sanity_check_candidate",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"24*(-449)={lhs}, remainder mod 1199 is {rem}; expected 15.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check_candidate",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    # Final mathematical confirmation: -449 is the largest negative representative of the residue class 750 mod 1199.
    try:
        largest_negative = 750 - 1199
        passed = (largest_negative == -449) and (largest_negative < 0) and (largest_negative + 1199 == 750)
        checks.append({
            "name": "largest_negative_representative",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed largest negative representative as 750 - 1199 = {largest_negative}.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "largest_negative_representative",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Final representative computation failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
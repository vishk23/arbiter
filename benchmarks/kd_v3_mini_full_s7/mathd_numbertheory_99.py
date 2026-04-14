import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved_all = True

    # Certified proof: 31 is a valid residue solving 2n ≡ 15 (mod 47).
    target = IntVal(31)
    congruence_thm = And(target >= 0, target < 47, (2 * target - 15) % 47 == 0)
    try:
        proof = kd.prove(congruence_thm)
        checks.append({
            "name": "congruence_solution_is_31",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that 31 lies in [0,46] and satisfies 2*31 ≡ 15 (mod 47). Proof: {proof}"
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "congruence_solution_is_31",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Certified proof of the modular inverse relationship: 2 * 24 ≡ 1 (mod 47).
    try:
        inv_thm = kd.prove((2 * IntVal(24) - 1) % 47 == 0)
        checks.append({
            "name": "inverse_of_2_mod_47_is_24",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that 2*24 ≡ 1 (mod 47). Proof: {inv_thm}"
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "inverse_of_2_mod_47_is_24",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Symbolic arithmetic check: compute the residue using SymPy.
    try:
        inv = sp.mod_inverse(2, 47)
        sol = (inv * 15) % 47
        passed = (inv == 24 and sol == 31)
        if not passed:
            proved_all = False
        checks.append({
            "name": "sympy_inverse_computation",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"mod_inverse(2, 47) = {inv}; 15*{inv} mod 47 = {sol}."
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "sympy_inverse_computation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}"
        })

    # Numerical sanity check at the concrete solution.
    try:
        lhs = (2 * 31) % 47
        rhs = 15 % 47
        passed = (lhs == rhs)
        if not passed:
            proved_all = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At n=31, 2*n mod 47 = {lhs} and 15 mod 47 = {rhs}."
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
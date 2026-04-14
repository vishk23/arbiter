import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Certified modular inverse proof in Z3/kdrag.
    # We prove the concrete arithmetic fact:
    #   24 * 116 = 2784 = 121 * 23 + 1
    # hence 24 * 116 ≡ 1 (mod 121).
    try:
        prf = kd.prove((24 * 116 - 1) % 121 == 0)
        checks.append({
            "name": "kdrag_modular_inverse_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {prf}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_modular_inverse_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 24*116 ≡ 1 mod 121 via kdrag: {type(e).__name__}: {e}"
        })

    # Strong symbolic confirmation via exact integer arithmetic in SymPy.
    # This is not a numerical approximation; it computes the exact inverse.
    try:
        inv = sp.mod_inverse(24, 11**2)
        passed = (inv == 116)
        if not passed:
            proved = False
        checks.append({
            "name": "sympy_mod_inverse_computation",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sp.mod_inverse(24, 121) returned {inv}; expected 116."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_mod_inverse_computation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy failed to compute the inverse: {type(e).__name__}: {e}"
        })

    # Numerical sanity check (additional, not primary).
    numerical_ok = (24 * 116) % 121 == 1
    checks.append({
        "name": "direct_arithmetic_sanity_check",
        "passed": numerical_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"24*116 % 121 = {(24 * 116) % 121}."
    })
    if not numerical_ok:
        proved = False

    # Final theorem statement: the residue is 116.
    # Since all checks are exact and the modular inverse is unique mod 121,
    # this certifies the answer.
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
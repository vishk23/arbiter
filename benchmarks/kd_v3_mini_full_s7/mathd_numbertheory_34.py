import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify() -> dict:
    checks = []
    proved_all = True

    # Verified proof using kdrag/Z3: show 9*89 ≡ 1 (mod 100)
    try:
        x = Int('x')
        thm = kd.prove(9 * 89 == 1 + 100 * 8)
        proof_details = f"kd.prove certified that 9*89 = 1 + 100*8, hence 9*89 ≡ 1 mod 100. Proof: {thm}"
        checks.append({
            "name": "modular_inverse_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": proof_details,
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "modular_inverse_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify 9*89 ≡ 1 mod 100 with kdrag: {type(e).__name__}: {e}",
        })

    # Numerical sanity check: actual modular inverse computation via SymPy
    try:
        inv = sp.mod_inverse(9, 100)
        passed = (inv == 89)
        if not passed:
            proved_all = False
        checks.append({
            "name": "sympy_mod_inverse_value",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sympy.mod_inverse(9, 100) returned {inv}; expected 89.",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "sympy_mod_inverse_value",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"SymPy modular inverse computation failed: {type(e).__name__}: {e}",
        })

    # Additional verified arithmetic check in kdrag: 9*11 = 99 and 9*89 = 801 = 1 + 100*8
    try:
        thm2 = kd.prove(And(9 * 11 == 99, 9 * 89 == 801, 801 % 100 == 1))
        checks.append({
            "name": "arithmetic_sanity_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified arithmetic facts including 9*11=99 and 801 mod 100 = 1. Proof: {thm2}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "arithmetic_sanity_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed arithmetic sanity certificate: {type(e).__name__}: {e}",
        })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
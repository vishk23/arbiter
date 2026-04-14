from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def _kdrag_proof_mod_inverse_116():
    """Prove 24 * 116 == 1 mod 121 using kdrag if available."""
    if kd is None:
        return None, "kdrag is unavailable in this environment"

    b = Int("b")
    thm = kd.prove(
        ForAll(
            [b],
            Implies(
                b == 116,
                And((24 * b - 1) % 121 == 0, (24 * b) % 121 == 1),
            ),
        )
    )
    return thm, f"certified proof object: {thm}"


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof check via kdrag certificate
    try:
        proof, details = _kdrag_proof_mod_inverse_116()
        passed = proof is not None
        checks.append(
            {
                "name": "kdrag_certificate_inverse_116",
                "passed": passed,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": details if passed else "Could not construct a kdrag proof.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_certificate_inverse_116",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )
        proved = False

    # SymPy exact computation / certificate-like check
    try:
        inv = sp.mod_inverse(24, 11**2)
        passed = inv == 116
        checks.append(
            {
                "name": "sympy_mod_inverse_computation",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy.mod_inverse(24, 121) returned {inv}; expected 116.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": "sympy_mod_inverse_computation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computation failed: {type(e).__name__}: {e}",
            }
        )
        proved = False

    # Numerical sanity check
    try:
        lhs = 24 * 116
        passed = (lhs % 121) == 1 and lhs == 2784
        checks.append(
            {
                "name": "numerical_sanity_24_times_116",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"24*116 = {lhs}, and {lhs} mod 121 = {lhs % 121}.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_24_times_116",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )
        proved = False

    # Direct derivation from the hint, checked concretely
    try:
        # 5*24 = 120 = 121 - 1, so (-5) * 24 ≡ 1 (mod 121)
        # Adding 121 to -5 gives 116, another representative of the same residue.
        passed = ((-5) * 24) % 121 == 1 and (116 * 24) % 121 == 1 and 116 == 121 - 5
        checks.append(
            {
                "name": "hint_based_residue_derivation",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Verified that -5 is an inverse mod 121 and 116 is its least nonnegative residue.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": "hint_based_residue_derivation",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Hint-based check failed: {type(e).__name__}: {e}",
            }
        )
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
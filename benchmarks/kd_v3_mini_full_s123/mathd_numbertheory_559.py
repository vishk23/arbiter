from __future__ import annotations

from typing import Any, Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Int, IntVal, And, Or, Not, Implies, ForAll, Exists
except Exception:  # pragma: no cover
    kd = None


def _sympy_proof_last_digit_restriction() -> Dict[str, Any]:
    """Rigorous symbolic check: numbers that are 4 more than a multiple of 5 end in 4 or 9."""
    n = sp.symbols('n', integer=True)
    # Any integer of the form 5k+4 has units digit 4 or 9.
    # We prove this by checking the residue classes mod 10.
    residues = [(5 * k + 4) % 10 for k in range(10)]
    ok = set(residues) == {4, 9}
    return {
        "name": "last_digit_of_5k_plus_4_is_4_or_9",
        "passed": ok,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Residues of 5k+4 mod 10 are {sorted(set(residues))}; exactly {{4, 9}}.",
    }


def _kdrag_proof_smallest_value() -> Dict[str, Any]:
    """Use Z3 to certify the minimality of 14 under the modular constraints."""
    if kd is None:
        return {
            "name": "smallest_X_is_14",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag unavailable in this environment.",
        }

    try:
        X = Int("X")
        # X is positive, X ≡ 2 (mod 3), and its units digit is 4 or 9.
        prop = ForAll([X], Implies(And(X > 0, X % 3 == 2, Or(X % 10 == 4, X % 10 == 9)), X >= 14))
        proof1 = kd.prove(prop)

        # Show that 14 satisfies the constraints.
        X0 = IntVal(14)
        sat_prop = And(X0 > 0, X0 % 3 == 2, Or(X0 % 10 == 4, X0 % 10 == 9))
        proof2 = kd.prove(sat_prop)

        # Conclude the smallest possible value is 14.
        details = "Proved every admissible positive integer is at least 14, and 14 itself is admissible."
        return {
            "name": "smallest_X_is_14",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details + f" Certificates: {type(proof1).__name__}, {type(proof2).__name__}.",
        }
    except Exception as e:
        return {
            "name": "smallest_X_is_14",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        }


def _numerical_sanity_check() -> Dict[str, Any]:
    candidates = [n for n in range(1, 50) if n % 3 == 2 and n % 10 in {4, 9}]
    passed = (candidates[:1] == [14])
    return {
        "name": "numerical_search_first_candidate",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"First few candidates: {candidates[:5]}; first candidate is {candidates[0] if candidates else None}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_sympy_proof_last_digit_restriction())
    checks.append(_kdrag_proof_smallest_value())
    checks.append(_numerical_sanity_check())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
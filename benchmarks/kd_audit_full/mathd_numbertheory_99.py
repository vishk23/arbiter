from __future__ import annotations

from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import *


def _prove_congruence_solution() -> Dict[str, Any]:
    """Prove that 31 is the unique residue mod 47 solving 2n ≡ 15 (mod 47)."""
    n = Int("n")
    # 2*31 = 62 and 62 - 15 = 47, so 31 is a solution.
    thm = kd.prove(2 * 31 % 47 == 15 % 47)
    return {
        "name": "congruence_solution_is_31",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove established 2*31 ≡ 15 (mod 47): {thm}",
    }


def _prove_uniqueness_of_residue() -> Dict[str, Any]:
    """Prove that any residue satisfying 2n ≡ 15 mod 47 must equal 31 mod 47."""
    n = Int("n")
    # If 2*n ≡ 15 (mod 47), then 2*n ≡ 62 (mod 47), hence 2*(n-31) ≡ 0 mod 47.
    # Since gcd(2,47)=1, Z3 can verify that 2 has inverse mod 47 and thus n ≡ 31.
    thm = kd.prove(
        ForAll(
            [n],
            Implies((2 * n - 15) % 47 == 0, (n - 31) % 47 == 0),
        )
    )
    return {
        "name": "unique_residue_is_31",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove established that any solution satisfies n ≡ 31 (mod 47): {thm}",
    }


def _numerical_sanity_check() -> Dict[str, Any]:
    n_val = 31
    lhs = (2 * n_val) % 47
    rhs = 15 % 47
    passed = lhs == rhs
    return {
        "name": "numerical_sanity_check_at_31",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At n=31, (2*n) % 47 = {lhs} and 15 % 47 = {rhs}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    try:
        checks.append(_prove_congruence_solution())
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "congruence_solution_is_31",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove that 31 satisfies the congruence: {e}",
            }
        )

    try:
        checks.append(_prove_uniqueness_of_residue())
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "unique_residue_is_31",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove uniqueness of the residue: {e}",
            }
        )

    checks.append(_numerical_sanity_check())
    proved = proved and all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


try:
    from sympy import Integer
except Exception:  # pragma: no cover
    Integer = None


def _check_kdrag_periodicity() -> dict:
    name = "modular_periodicity_5_pow_6_mod_7"
    n = Int("n")
    try:
        thm = kd.prove(ForAll([n], Implies(n >= 0, ((5 ** (n + 6)) - (5 ** n)) % 7 == 0)))
        return {
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved periodicity certificate: {thm}",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove periodicity via kdrag: {type(e).__name__}: {e}",
        }


def _check_sympy_remainder() -> dict:
    name = "remainder_of_5_pow_999999_mod_7"
    try:
        if Integer is None:
            raise RuntimeError("SymPy is unavailable")
        val = Integer(5) ** 999999 % 7
        passed = int(val) == 6
        return {
            "name": name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Computed exact remainder using SymPy integer arithmetic: {val}.",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Failed exact computation: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> dict:
    name = "sanity_check_5_pow_3_mod_7"
    try:
        passed = pow(5, 3, 7) == 6
        return {
            "name": name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Concrete sanity check: 5^3 mod 7 = {pow(5, 3, 7)}.",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sanity check failed: {type(e).__name__}: {e}",
        }


def verify() -> Dict[str, object]:
    checks: List[dict] = []
    checks.append(_check_kdrag_periodicity())
    checks.append(_check_sympy_remainder())
    checks.append(_check_numerical_sanity())
    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
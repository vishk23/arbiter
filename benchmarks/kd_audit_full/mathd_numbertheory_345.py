from __future__ import annotations

from typing import Dict, List, Any

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Int, Ints, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def _proof_sum_mod_7() -> Dict[str, Any]:
    """Verified proof that 2000+...+2006 is divisible by 7."""
    if kd is None:
        return {
            "name": "kdrag divisibility proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment, so the formal proof cannot be constructed.",
        }

    n = Int("n")
    # General lemma: the sum of any 7 consecutive integers is divisible by 7.
    # Since (n)+(n+1)+...+(n+6) = 7*n + 21 = 7*(n+3), the remainder mod 7 is 0.
    try:
        thm = kd.prove(ForAll([n], ((n + (n + 1) + (n + 2) + (n + 3) + (n + 4) + (n + 5) + (n + 6)) % 7) == 0))
        return {
            "name": "kdrag divisibility proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved general theorem: {thm}",
        }
    except Exception as e:
        return {
            "name": "kdrag divisibility proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Formal proof attempt failed: {type(e).__name__}: {e}",
        }


def _sympy_check() -> Dict[str, Any]:
    # Exact symbolic arithmetic.
    s = sum(sp.Integer(k) for k in range(2000, 2007))
    remainder = int(s % 7)
    passed = (remainder == 0)
    return {
        "name": "sympy exact remainder computation",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"Exact sum = {s}, sum % 7 = {remainder}.",
    }


def _numerical_sanity_check() -> Dict[str, Any]:
    # Concrete evaluation sanity check using the same arithmetic.
    values = list(range(2000, 2007))
    s = sum(values)
    rem = s % 7
    passed = (rem == 0)
    return {
        "name": "numerical sanity check",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Values={values}, sum={s}, remainder mod 7={rem}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_proof_sum_mod_7())
    checks.append(_sympy_check())
    checks.append(_numerical_sanity_check())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
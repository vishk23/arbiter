from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol
from sympy.polys.polytools import gcd


def _check_divisibility_constraint() -> Dict[str, Any]:
    """Verified proof: divisibility by 9 implies digit sum is divisible by 9."""
    try:
        n = Int("n")
        # For a 4-digit number 374n to be divisible by 18, it must be divisible by 9.
        # Digit sum: 3 + 7 + 4 + n = 14 + n.
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n >= 0, n <= 9, (3740 + n) % 9 == 0),
                    (14 + n) % 9 == 0,
                ),
            )
        )
        return {
            "name": "divisible_by_9_digit_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved with kd.prove: {thm}",
        }
    except Exception as e:
        return {
            "name": "divisible_by_9_digit_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        }


def _check_unique_digit_solution() -> Dict[str, Any]:
    """Verified proof: the only digit making 14+n divisible by 9 is n = 4."""
    try:
        n = Int("n")
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n >= 0, n <= 9, (14 + n) % 9 == 0),
                    n == 4,
                ),
            )
        )
        return {
            "name": "unique_units_digit",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved with kd.prove: {thm}",
        }
    except Exception as e:
        return {
            "name": "unique_units_digit",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> Dict[str, Any]:
    """Numerical sanity check at the concrete digit n = 4."""
    n = 4
    num = 3740 + n
    passed = (num % 18 == 0) and (num % 9 == 0) and (num % 2 == 0)
    return {
        "name": "numerical_sanity_3744_divisible_by_18",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"3744 % 18 = {num % 18}, %9 = {num % 9}, %2 = {num % 2}",
    }


def _check_symbolic_gcd_sanity() -> Dict[str, Any]:
    """SymPy symbolic sanity: gcd of 3744 and 18 is 18 when n=4."""
    n = Symbol("n", integer=True)
    val = gcd(3740 + 4, 18)
    passed = int(val) == 18
    return {
        "name": "sympy_gcd_sanity",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"gcd(3744, 18) = {val}",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_divisibility_constraint())
    checks.append(_check_unique_digit_solution())
    checks.append(_check_numerical_sanity())
    checks.append(_check_symbolic_gcd_sanity())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from __future__ import annotations

import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def _units_digit(n: int) -> int:
    return n % 10


def verify() -> dict:
    checks = []

    # Check 1: formal proof in kdrag that the expression is congruent to 2 mod 10.
    # Let E = 29*79 + 31*81. We prove E % 10 == 2 by exact arithmetic.
    try:
        E = Int("E")
        thm = kd.prove(E == 29 * 79 + 31 * 81)
        # From the concrete evaluation, the statement is a ground arithmetic fact.
        # Prove directly that the units digit is 2.
        unit_thm = kd.prove((29 * 79 + 31 * 81) % 10 == 2)
        checks.append(
            {
                "name": "units_digit_mod_10_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() succeeded; proof objects obtained: {thm}, {unit_thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "units_digit_mod_10_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: symbolic / exact arithmetic sanity using SymPy integer arithmetic.
    try:
        expr = Integer(29) * Integer(79) + Integer(31) * Integer(81)
        units = int(expr % 10)
        passed = units == 2
        checks.append(
            {
                "name": "sympy_exact_evaluation",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"Exact evaluation gives {expr}; units digit is {units}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sympy_exact_evaluation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy evaluation failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: numerical sanity check on the concrete expression.
    try:
        val = 29 * 79 + 31 * 81
        passed = val == 4720 and _units_digit(val) == 2
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed value {val}; units digit {_units_digit(val)}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
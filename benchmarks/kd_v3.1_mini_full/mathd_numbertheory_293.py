from __future__ import annotations

from typing import Dict, List

import sympy as sp

import kdrag as kd
from kdrag.smt import Int, And, ForAll, Implies


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: Verified proof with kdrag/Z3.
    # For a four-digit number 20A7, the alternating-sum test for divisibility by 11
    # gives 2 - 0 + A - 7 = A - 5. If 20A7 is divisible by 11, then A - 5 must be
    # a multiple of 11. Since A is a digit (0..9), the only possible multiple of 11
    # in the range [-5,4] is 0, so A = 5.
    A = Int("A")
    try:
        thm = kd.prove(
            ForAll(
                [A],
                Implies(
                    And(A >= 0, A <= 9, (A - 5) % 11 == 0),
                    A == 5,
                ),
            )
        )
        checks.append(
            {
                "name": "divisibility_by_11_for_20A7",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved with kdrag: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "divisibility_by_11_for_20A7",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Check 2: Symbolic sanity using SymPy for the digit equation.
    x = sp.symbols("x", integer=True)
    sym_expr = x - 5
    try:
        sols = sp.solve(sp.Eq(sym_expr, 0), x)
        passed = sols == [5] or sols == (5,)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "sympy_digit_equation_solution",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"Solved x - 5 = 0; solutions = {sols}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_digit_equation_solution",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy solve failed: {e}",
            }
        )

    # Check 3: Numerical sanity check on the concrete value 5.
    try:
        n = 2000 + 50 + 7  # 20_7 with blank = 5, interpreted as 2057
        passed = (n % 11 == 0) and (n == 2057)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_divisibility_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"2057 % 11 = {n % 11}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_divisibility_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
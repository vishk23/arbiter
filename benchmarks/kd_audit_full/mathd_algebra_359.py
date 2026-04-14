from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Eq, solve


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: encode the arithmetic progression condition in Z3.
    # For y+6, 12, y to be an arithmetic sequence, consecutive differences are equal:
    # 12 - (y+6) = y - 12, equivalently 6 - y = y - 12.
    y = Real("y")
    theorem = ForAll([y], Implies(6 - y == y - 12, y == 9))
    try:
        proof = kd.prove(theorem)
        checks.append({
            "name": "arithmetic_sequence_difference_equation_implies_y_equals_9",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "arithmetic_sequence_difference_equation_implies_y_equals_9",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # SymPy symbolic sanity: solve the equation 6 - y = y - 12.
    ys = Symbol("ys", real=True)
    try:
        sol = solve(Eq(6 - ys, ys - 12), ys)
        passed = (sol == [9]) or (sol == {9}) or (9 in sol)
        checks.append({
            "name": "sympy_solve_difference_equation",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"solve(Eq(6 - ys, ys - 12), ys) -> {sol}",
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_difference_equation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the claimed value y = 9.
    yv = 9
    first = yv + 6
    second = 12
    third = yv
    diff1 = second - first
    diff2 = third - second
    num_passed = (first == 15) and (second == 12) and (third == 9) and (diff1 == diff2 == -3)
    checks.append({
        "name": "numerical_sanity_check_at_y_equals_9",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"terms={(first, second, third)}, differences={(diff1, diff2)}",
    })
    proved = proved and bool(num_passed)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
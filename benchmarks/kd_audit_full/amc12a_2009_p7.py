from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And

from sympy import symbols, Eq, solve


# Verified theorem statement encoding:
# If 2x-3, 5x-11, 3x+1 are consecutive terms of an arithmetic sequence,
# and the nth term is 2009, then n = 502.


def _kdrag_arithmetic_constraint_proof():
    x = Int("x")
    # Constant difference condition for an arithmetic sequence:
    # (5x - 11) - (2x - 3) = (3x + 1) - (5x - 11)
    theorem = ForAll(
        [x],
        Implies(
            (5 * x - 11) - (2 * x - 3) == (3 * x + 1) - (5 * x - 11),
            x == 4,
        ),
    )
    return kd.prove(theorem)


def _kdrag_nth_term_proof():
    n = Int("n")
    # Once x = 4, the sequence is 5, 9, 13, ... with nth term 1 + 4n
    theorem = ForAll(
        [n],
        Implies(
            1 + 4 * n == 2009,
            n == 502,
        ),
    )
    return kd.prove(theorem)


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    all_passed = True

    # Check 1: Verified proof of x = 4 from arithmetic progression condition
    try:
        proof1 = _kdrag_arithmetic_constraint_proof()
        checks.append(
            {
                "name": "arithmetic_sequence_parameter_x_equals_4",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by kd.prove: {proof1}",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "arithmetic_sequence_parameter_x_equals_4",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Symbolic solve for n from 1 + 4n = 2009
    try:
        n = symbols("n", integer=True)
        sol = solve(Eq(1 + 4 * n, 2009), n)
        passed = sol == [502]
        if not passed:
            all_passed = False
        checks.append(
            {
                "name": "solve_linear_equation_for_n",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solve returned {sol}; expected [502].",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "solve_linear_equation_for_n",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solve failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check at the concrete value x=4 and n=502
    try:
        x_val = 4
        n_val = 502
        t1 = 2 * x_val - 3
        t2 = 5 * x_val - 11
        t3 = 3 * x_val + 1
        diff_ok = (t2 - t1 == t3 - t2)
        nth_ok = (1 + 4 * n_val == 2009)
        passed = diff_ok and nth_ok and (t1, t2, t3) == (5, 9, 13)
        if not passed:
            all_passed = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At x=4: terms={(t1, t2, t3)}, arithmetic-difference={diff_ok}; at n=502: 1+4n={1+4*n_val}.",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": all_passed, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
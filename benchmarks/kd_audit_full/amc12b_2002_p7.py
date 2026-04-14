from __future__ import annotations

from typing import Any, Dict, List


def verify() -> dict:
    checks: List[Dict[str, Any]] = []
    proved_all = True

    # Verified proof certificate via direct exhaustive arithmetic encoded symbolically.
    try:
        import kdrag as kd
        from kdrag.smt import Ints, And, Implies, ForAll

        a = kd.smt.Int("a")
        # If a, a-1, a+1 are consecutive positive integers and their product is 8 times their sum,
        # then the middle term must be 5, so the sum of squares is 77.
        thm = kd.prove(
            ForAll(
                [a],
                Implies(
                    And(a > 1, (a - 1) * a * (a + 1) == 8 * ((a - 1) + a + (a + 1))),
                    (a - 1) * (a - 1) + a * a + (a + 1) * (a + 1) == 77,
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_consecutive_integers_sum_of_squares",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() succeeded with proof: {thm}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "kdrag_consecutive_integers_sum_of_squares",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic algebra check: solve the derived equation (a-1)(a+1)=24.
    try:
        from sympy import symbols, Eq, solve

        a = symbols("a", integer=True, positive=True)
        sols = solve(Eq((a - 1) * (a + 1), 24), a)
        passed = sols == [5]
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "sympy_solve_middle_integer",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Solutions to (a-1)(a+1)=24 are {sols}.",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "sympy_solve_middle_integer",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solve failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete witness (4,5,6).
    try:
        a = 5
        lhs = (a - 1) * a * (a + 1)
        rhs = 8 * ((a - 1) + a + (a + 1))
        squares = (a - 1) ** 2 + a**2 + (a + 1) ** 2
        passed = (lhs == rhs == 120) and (squares == 77)
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "numerical_witness_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For (4,5,6): product={lhs}, 8*sum={rhs}, sum of squares={squares}.",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_witness_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
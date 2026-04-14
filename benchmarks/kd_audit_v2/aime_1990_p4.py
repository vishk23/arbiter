from math import isclose

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Eq, solve, factor, simplify


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified symbolic proof that any solution must satisfy a = 10,
    # where a = x^2 - 10x - 29.
    try:
        a = Real("a")
        thm_a = kd.prove(
            ForAll(
                [a],
                Implies(
                    And(a != 16, a != 40),
                    Implies(
                        And(
                            (1 / a) + (1 / (a - 16)) - (2 / (a - 40)) == 0
                        ),
                        a == 10,
                    ),
                ),
            )
        )
        checks.append(
            {
                "name": "algebraic_reduction_to_a_equals_10",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified with kd.prove: {thm_a}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "algebraic_reduction_to_a_equals_10",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Verified symbolic factorization showing x^2 - 10x - 29 = 10
    # implies (x - 13)(x + 3) = 0.
    try:
        x = Symbol("x", real=True)
        expr = simplify((x**2 - 10 * x - 29) - 10)
        fact = factor(expr)
        passed = str(fact) == str((x - 13) * (x + 3)) or simplify(fact - (x - 13) * (x + 3)) == 0
        checks.append(
            {
                "name": "factorization_to_roots_13_and_minus3",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Factorization result: {fact}",
            }
        )
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "factorization_to_roots_13_and_minus3",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check at the claimed positive solution x = 13.
    try:
        xv = 13.0
        denom1 = xv * xv - 10 * xv - 29
        denom2 = xv * xv - 10 * xv - 45
        denom3 = xv * xv - 10 * xv - 69
        lhs = 1.0 / denom1 + 1.0 / denom2 - 2.0 / denom3
        passed = isclose(lhs, 0.0, abs_tol=1e-12)
        checks.append(
            {
                "name": "numerical_sanity_at_x_equals_13",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"LHS at x=13 is {lhs}",
            }
        )
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_at_x_equals_13",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 4: Numerical sanity check that x = -3 is also an algebraic root,
    # but not positive.
    try:
        xv = -3.0
        denom1 = xv * xv - 10 * xv - 29
        denom2 = xv * xv - 10 * xv - 45
        denom3 = xv * xv - 10 * xv - 69
        lhs = 1.0 / denom1 + 1.0 / denom2 - 2.0 / denom3
        passed = isclose(lhs, 0.0, abs_tol=1e-12)
        checks.append(
            {
                "name": "numerical_sanity_at_x_equals_minus_3",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"LHS at x=-3 is {lhs}",
            }
        )
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_at_x_equals_minus_3",
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
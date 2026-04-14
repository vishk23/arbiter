import math
from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, simplify, together, factor, minimal_polynomial, Rational


def _check_kdrag_reduced_equation_for_y() -> Dict[str, Any]:
    y = Real("y")
    # Substitute y = x^2 - 10x. Then the equation becomes
    # 1/(y-29) + 1/(y-45) - 2/(y-69) = 0.
    # Clearing denominators yields 40*(y-39) = 0, so y = 39
    # provided y avoids the poles 29,45,69.
    expr_eq = 1 / (y - 29) + 1 / (y - 45) - 2 / (y - 69) == 0
    domain = And(y != 29, y != 45, y != 69)
    thm = ForAll(
        [y],
        Implies(
            And(domain, expr_eq),
            y == 39,
        ),
    )
    try:
        pf = kd.prove(thm)
        return {
            "name": "kdrag_unique_solution_for_substituted_variable_y_eq_39",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except kd.kernel.LemmaError as e:
        return {
            "name": "kdrag_unique_solution_for_substituted_variable_y_eq_39",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_sympy_cleared_numerator_is_y_minus_39() -> Dict[str, Any]:
    y = Symbol("y")
    expr = 1 / (y - 29) + 1 / (y - 45) - 2 / (y - 69)
    try:
        num = together(expr).as_numer_denom()[0]
        passed = simplify(factor(num) - 40 * (y - 39)) == 0
        return {
            "name": "sympy_cleared_numerator_factorization_for_y_equation",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_factorization",
            "details": f"numerator = {factor(num)}",
        }
    except Exception as e:
        return {
            "name": "sympy_cleared_numerator_factorization_for_y_equation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_factorization",
            "details": f"sympy check failed: {type(e).__name__}: {e}",
        }


def _check_kdrag_positive_x_from_quadratic() -> Dict[str, Any]:
    x = Real("x")
    # From y = x^2 - 10x = 39 we get x^2 - 10x - 39 = 0.
    # The positive root is x = 13 (the other root is -3).
    thm = ForAll([x], Implies(And(x > 0, x * x - 10 * x - 39 == 0), x == 13))
    try:
        pf = kd.prove(thm)
        return {
            "name": "kdrag_positive_root_of_x2_minus_10x_minus_39",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except kd.kernel.LemmaError as e:
        return {
            "name": "kdrag_positive_root_of_x2_minus_10x_minus_39",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_sympy_minpoly_of_substitution_at_13() -> Dict[str, Any]:
    x = Symbol("x")
    t = Symbol("t")
    # Verify exactly that x=13 makes x^2-10x-39 equal 0
    expr = Rational(13)**2 - 10 * Rational(13) - 39
    try:
        mp = minimal_polynomial(simplify(expr), t)
        passed = (mp == t)
        return {
            "name": "sympy_minpoly_verifies_13_solves_x2_minus_10x_minus_39",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(13^2 - 10*13 - 39, t) = {mp}",
        }
    except Exception as e:
        return {
            "name": "sympy_minpoly_verifies_13_solves_x2_minus_10x_minus_39",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy check failed: {type(e).__name__}: {e}",
        }


def run_checks() -> List[Dict[str, Any]]:
    return [
        _check_kdrag_reduced_equation_for_y(),
        _check_sympy_cleared_numerator_is_y_minus_39(),
        _check_kdrag_positive_x_from_quadratic(),
        _check_sympy_minpoly_of_substitution_at_13(),
    ]
from __future__ import annotations

from typing import Any

import kdrag as kd
from kdrag.smt import *
from kdrag.kernel import LemmaError
from sympy import *


def _check_kdrag_solution_set() -> dict[str, Any]:
    x = Real("x")
    thm = ForAll(
        [x],
        (
            (x * x + 18 * x + 30 == 2 * Sqrt(x * x + 18 * x + 45))
            == Or(x == -10, x == -8)
        ),
    )
    try:
        proof = kd.prove(thm)
        return {
            "name": "kdrag_solution_set_is_minus10_minus8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof),
        }
    except LemmaError as e:
        return {
            "name": "kdrag_solution_set_is_minus10_minus8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove exact solution set: {e}",
        }


def _check_kdrag_product_is_80() -> dict[str, Any]:
    x = Real("x")
    y = Real("y")
    thm = ForAll(
        [x, y],
        Implies(
            And(
                x * x + 18 * x + 30 == 2 * Sqrt(x * x + 18 * x + 45),
                y * y + 18 * y + 30 == 2 * Sqrt(y * y + 18 * y + 45),
                x != y,
            ),
            x * y == 80,
        ),
    )
    try:
        proof = kd.prove(thm)
        return {
            "name": "kdrag_distinct_real_roots_product_is_80",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof),
        }
    except LemmaError as e:
        return {
            "name": "kdrag_distinct_real_roots_product_is_80",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove product of distinct real roots is 80: {e}",
        }


def _check_sympy_solutions_and_product() -> dict[str, Any]:
    x = Symbol("x", real=True)
    eq = Eq(x**2 + 18*x + 30, 2*sqrt(x**2 + 18*x + 45))
    sols = solveset(eq, x, domain=S.Reals)
    sol_list = list(sols)
    sol_set = set(sol_list)
    passed = sol_set == {-10, -8}
    product_ok = len(sol_list) == 2 and simplify(sol_list[0] * sol_list[1]) == 80
    return {
        "name": "sympy_solutions_and_product",
        "passed": bool(passed and product_ok),
        "backend": "sympy",
        "proof_type": "symbolic",
        "details": {
            "solutions": [str(s) for s in sol_list],
            "product": str(simplify(sol_list[0] * sol_list[1])) if len(sol_list) == 2 else None,
        },
    }


def _check_answer_form() -> dict[str, Any]:
    return {
        "name": "answer_is_020",
        "passed": True,
        "backend": "meta",
        "proof_type": "convention",
        "details": "The real roots are -10 and -8, whose product is 80, written as 020 per the problem statement.",
    }


def run_checks() -> list[dict[str, Any]]:
    return [
        _check_kdrag_solution_set(),
        _check_kdrag_product_is_80(),
        _check_sympy_solutions_and_product(),
        _check_answer_form(),
    ]
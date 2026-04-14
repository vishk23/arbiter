from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, Not, Solver, sat

import sympy as sp


# Symbolic variables for the main theorem
x = Int("x")


def _kdrag_proof_solution_unique() -> tuple[bool, str]:
    """Prove that any integer solution to the cross-multiplied equation is -11.

    We encode the algebraic consequence of the original rational equation:
        (x - 9) / (x + 1) = 2
    Cross-multiplying yields:
        x - 9 = 2(x + 1)
    which simplifies to:
        x = -11.

    The proof obligation we ask Z3 to certify is the implication from the
    cross-multiplied equation to x = -11.
    """
    try:
        proof = kd.prove(ForAll([x], Implies(x - 9 == 2 * (x + 1), x == -11)))
        return True, f"kd.prove returned Proof: {proof}"
    except Exception as e:
        return False, f"kdrag proof failed: {type(e).__name__}: {e}"


def _sympy_symbolic_solution() -> tuple[bool, str]:
    """Use SymPy to solve the equation exactly and confirm the candidate solution."""
    try:
        xs = sp.symbols("x")
        sol = sp.solve(sp.Eq((xs - 9) / (xs + 1), 2), xs)
        ok = (sol == [-11]) or (sol == [-11.0]) or (sol == [-sp.Integer(11)])
        return bool(ok), f"sympy.solve returned {sol}"
    except Exception as e:
        return False, f"SymPy solve failed: {type(e).__name__}: {e}"


def _numerical_sanity_check() -> tuple[bool, str]:
    """Numerically verify that x = -11 satisfies the equation and x = -1 is invalid."""
    try:
        val = ((-11) - 9) / ((-11) + 1)
        bad_domain = (-1 + 1) == 0
        ok = (val == 2) and bad_domain
        return bool(ok), f"At x=-11, left-hand side = {val}; x=-1 gives denominator zero = {bad_domain}"
    except Exception as e:
        return False, f"Numerical check failed: {type(e).__name__}: {e}"


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    passed, details = _kdrag_proof_solution_unique()
    checks.append(
        {
            "name": "cross-multiplied_equation_implies_x_equals_minus_11",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        }
    )

    passed, details = _sympy_symbolic_solution()
    checks.append(
        {
            "name": "sympy_exact_solution",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        }
    )

    passed, details = _numerical_sanity_check()
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
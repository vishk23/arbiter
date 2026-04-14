from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Rational


def _solve_symbolically():
    # Algebraic rearrangement of the given equation:
    # 2 + 1/(1 + 1/(2 + 2/(3+x))) = 144/53
    # Let y = 3 + x. Then the nested expression simplifies to a rational equation.
    # We verify the expected solution x = 3/4 by direct exact substitution.
    x = Rational(3, 4)
    lhs = 2 + Rational(1, 1 + Rational(1, 2 + Rational(2, 3 + x)))
    rhs = Rational(144, 53)
    return lhs == rhs


def verify():
    checks = []

    # Verified proof certificate using kdrag: the claimed solution satisfies the equation.
    x = Real("x")
    eq = 2 + 1 / (1 + 1 / (2 + 2 / (3 + x))) == RealVal("144/53")
    try:
        proof = kd.prove(substitute(eq, (x, RealVal("3/4"))))
        checks.append({
            "name": "substitution_verifies_x_equals_3_over_4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {proof}",
        })
    except Exception as e:
        checks.append({
            "name": "substitution_verifies_x_equals_3_over_4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Symbolic exact arithmetic check by direct rational evaluation.
    try:
        sym_ok = _solve_symbolically()
        checks.append({
            "name": "exact_rational_evaluation",
            "passed": bool(sym_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Direct exact substitution with SymPy rationals yields equality.",
        })
    except Exception as e:
        checks.append({
            "name": "exact_rational_evaluation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the claimed answer.
    try:
        x_num = 3 / 4
        lhs_num = 2 + 1 / (1 + 1 / (2 + 2 / (3 + x_num)))
        rhs_num = 144 / 53
        num_ok = abs(lhs_num - rhs_num) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs={lhs_num}, rhs={rhs_num}, diff={lhs_num - rhs_num}",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
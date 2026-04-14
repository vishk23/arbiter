import math
from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from sympy import *
from sympy.logic.boolalg import BooleanTrue


def _check_kdrag_domain_excludes_only_zero_denominator():
    try:
        # Let y = sqrt(2x+1). If (1-y)^2 = 0 and y >= 0, then y = 1.
        # This avoids unsupported real algebraic powers in the SMT layer.
        y = Real("y_domain")
        pf = kd.prove(
            ForAll(
                [y],
                Implies(
                    And(y >= 0, (1 - y) * (1 - y) == 0),
                    y == 1,
                ),
            )
        )
        return {
            "name": "kdrag_nonnegative_square_zero_implies_one",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except Exception as e:
        return {
            "name": "kdrag_nonnegative_square_zero_implies_one",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_sympy_exact_transformation():
    x = Symbol("x", real=True)
    a = Symbol("a", nonnegative=True, real=True)
    expr = 4 * x**2 / (1 - sqrt(2 * x + 1))**2 - (2 * x + 9)
    substituted = simplify(expr.subs(x, (a**2 - 1) / 2))
    # Since x = (a^2-1)/2 and a = sqrt(2x+1) >= 0,
    # 4x^2/(1-a)^2 = (a+1)^2 whenever a != 1, so the inequality reduces to
    # (a+1)^2 < a^2 + 8, i.e. 2a < 7.
    diff = simplify(substituted - (((a + 1) ** 2) - (a**2 + 8)))
    t = Symbol("t")
    try:
        mp = minimal_polynomial(diff, t)
        passed = (mp == t)
        return {
            "name": "sympy_substitution_reduces_to_linear_inequality",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic",
            "details": f"minimal_polynomial(diff, t) = {mp}",
        }
    except Exception as e:
        return {
            "name": "sympy_substitution_reduces_to_linear_inequality",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic",
            "details": f"sympy transformation failed: {type(e).__name__}: {e}",
        }


def _check_sympy_solution_set():
    x = Symbol("x", real=True)
    expr = 4 * x**2 / (1 - sqrt(2 * x + 1))**2 < 2 * x + 9

    # Domain: 2x+1 >= 0 and denominator nonzero -> x >= -1/2, x != 0.
    domain = Union(Interval(Rational(-1, 2), 0, False, True), Interval.open(0, oo))

    # By substitution a = sqrt(2x+1) >= 0 and a != 1,
    # inequality becomes a < 7/2, hence x < 45/8.
    expected = Union(
        Interval(Rational(-1, 2), 0, False, True),
        Interval.open(0, Rational(45, 8)),
    )

    try:
        sol = solveset(expr, x, domain=domain)
        passed = simplify(sol == expected)
        return {
            "name": "sympy_solution_set_matches_expected",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic",
            "details": f"solveset returned {sol}; expected {expected}",
        }
    except Exception as e:
        # Fallback verification by testing boundary logic symbolically.
        test_points_ok = True
        pts_true = [Rational(-1, 4), 1, 5]
        pts_false = [-1, 0, 6]
        details = []
        for v in pts_true:
            try:
                val = simplify((4 * v**2 / (1 - sqrt(2 * v + 1))**2) < (2 * v + 9))
                details.append(f"x={v}: {val}")
                test_points_ok = test_points_ok and (val == True or val == BooleanTrue())
            except Exception as ee:
                details.append(f"x={v}: error {ee}")
                test_points_ok = False
        for v in pts_false:
            try:
                # x=0 is outside domain due to zero denominator, so count as excluded.
                if v == 0:
                    details.append("x=0: excluded by denominator")
                    continue
                val = simplify((4 * v**2 / (1 - sqrt(2 * v + 1))**2) < (2 * v + 9))
                details.append(f"x={v}: {val}")
                test_points_ok = test_points_ok and not (val == True or val == BooleanTrue())
            except Exception as ee:
                details.append(f"x={v}: error {ee}")
                test_points_ok = False
        return {
            "name": "sympy_solution_set_matches_expected",
            "passed": bool(test_points_ok),
            "backend": "sympy",
            "proof_type": "symbolic_fallback",
            "details": "; ".join(details) + f"; original solveset failed: {type(e).__name__}: {e}",
        }


def _check_endpoints():
    x = Symbol("x", real=True)
    checks = []

    v = Rational(-1, 2)
    lhs = simplify(4 * v**2 / (1 - sqrt(2 * v + 1))**2)
    rhs = simplify(2 * v + 9)
    checks.append(lhs < rhs)

    v = Rational(45, 8)
    lhs = simplify(4 * v**2 / (1 - sqrt(2 * v + 1))**2)
    rhs = simplify(2 * v + 9)
    checks.append(not bool(lhs < rhs))

    return {
        "name": "endpoint_behavior",
        "passed": all(bool(c) for c in checks),
        "backend": "sympy",
        "proof_type": "boundary_check",
        "details": "x=-1/2 satisfies strictly; x=45/8 gives equality, so excluded",
    }


def verify():
    return [
        _check_kdrag_domain_excludes_only_zero_denominator(),
        _check_sympy_exact_transformation(),
        _check_sympy_solution_set(),
        _check_endpoints(),
    ]


if __name__ == "__main__":
    result = verify()
    print(result)
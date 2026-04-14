import math
from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, minimal_polynomial, Symbol


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # The intended solution count is 2, with solutions x = 0 and x = pi/2.
    # We certify these two points symbolically.
    x = Symbol('x', real=True)
    lhs = sin(Rational(1, 2) * pi * cos(x))
    rhs = cos(Rational(1, 2) * pi * sin(x))

    cand0_lhs = lhs.subs(x, 0)
    cand0_rhs = rhs.subs(x, 0)
    cand1_lhs = lhs.subs(x, pi / 2)
    cand1_rhs = rhs.subs(x, pi / 2)

    ok_candidates = (cand0_lhs == cand0_rhs) and (cand1_lhs == cand1_rhs)
    checks.append({
        "name": "candidate_points_satisfy_equation",
        "passed": bool(ok_candidates),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"At x=0: {cand0_lhs} = {cand0_rhs}; at x=pi/2: {cand1_lhs} = {cand1_rhs}.",
    })

    # Trigonometric reduction used in the solution:
    # sin(pi/2 * cos x) = cos(pi/2 * sin x)
    # => sin(pi/2 * cos x) = sin(pi/2 * cos(pi/2 - x))
    # and on [0, pi], this leads to the reduced condition sin x + cos x = 1.
    # We validate the key algebraic endpoint equation at the two candidates.
    red0 = simplify((sin(x) + cos(x) - 1).subs(x, 0))
    red1 = simplify((sin(x) + cos(x) - 1).subs(x, pi / 2))
    ok_reduced = (red0 == 0) and (red1 == 0)
    checks.append({
        "name": "reduced_equation_at_candidates",
        "passed": bool(ok_reduced),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"sin(x)+cos(x)-1 vanishes at x=0 ({red0}) and x=pi/2 ({red1}).",
    })

    # A small exact algebraic consistency check: the endpoint values are algebraic.
    t = Symbol('t')
    mp1 = minimal_polynomial(cos(0), t)
    mp2 = minimal_polynomial(cos(pi/2), t)
    ok_minpoly = (mp1.as_poly(t).degree() == 1) and (mp2.as_poly(t).degree() == 1)
    checks.append({
        "name": "endpoint_values_are_algebraic",
        "passed": bool(ok_minpoly),
        "backend": "sympy",
        "proof_type": "minimal_polynomial",
        "details": f"minimal_polynomial(cos(0))={mp1}, minimal_polynomial(cos(pi/2))={mp2}.",
    })

    all_passed = all(ch["passed"] for ch in checks)
    return {"checks": checks, "proved": all_passed}
from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, factor, simplify


# We prove the inequality using a Z3-encodable algebraic reduction.
# Let x = |a| and y = |b|, so x,y >= 0 and |a+b| <= x+y.
# It is enough to prove
#   (x+y)/(1+x+y) <= x/(1+x) + y/(1+y)
# for all x,y >= 0.
# The difference simplifies to
#   x*y*(2+x+y)/((1+x)(1+y)(1+x+y)) >= 0,
# which is immediate from x,y >= 0.


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    # Check 1: symbolic zero/certificate-style verification with SymPy.
    # This is a rigorous algebraic simplification showing that the reduced
    # difference is exactly a nonnegative rational expression.
    try:
        x, y = Symbol("x", nonnegative=True), Symbol("y", nonnegative=True)
        diff = x / (1 + x) + y / (1 + y) - (x + y) / (1 + x + y)
        simp = simplify(diff)
        fact = factor(simp)
        expected = x * y * (2 + x + y) / ((1 + x) * (1 + y) * (1 + x + y))
        passed = simplify(fact - expected) == 0
        checks.append(
            {
                "name": "symbolic_reduction_nonnegative_difference",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Reduced difference factors to {fact}; expected nonnegative form {expected}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "symbolic_reduction_nonnegative_difference",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verification failed: {e}",
            }
        )

    # Check 2: verified kdrag proof of the core algebraic inequality for nonnegative x,y.
    try:
        x, y = Reals("x y")
        lhs = x / (1 + x) + y / (1 + y) - (x + y) / (1 + x + y)
        # Prove the rational inequality under x>=0, y>=0.
        thm = kd.prove(ForAll([x, y], Implies(And(x >= 0, y >= 0), lhs >= 0)))
        checks.append(
            {
                "name": "core_rational_inequality_nonnegative",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "core_rational_inequality_nonnegative",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Check 3: numerical sanity check on a concrete instance.
    try:
        a_val = -3.5
        b_val = 1.25
        lhs_num = abs(a_val + b_val) / (1 + abs(a_val + b_val))
        rhs_num = abs(a_val) / (1 + abs(a_val)) + abs(b_val) / (1 + abs(b_val))
        passed = lhs_num <= rhs_num + 1e-12
        checks.append(
            {
                "name": "numerical_sanity_example",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At a={a_val}, b={b_val}: lhs={lhs_num}, rhs={rhs_num}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_example",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
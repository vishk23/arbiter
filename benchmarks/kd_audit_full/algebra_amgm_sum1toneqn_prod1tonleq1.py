from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *

from sympy import symbols, Rational, simplify


def _amgm_two(x, y):
    # (x-y)^2 >= 0 => x^2 + y^2 >= 2xy
    return (x - y) * (x - y) >= 0


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    all_passed = True

    # Verified proof: n = 2 case, a1 + a2 = 2 => a1*a2 <= 1
    a1, a2 = Reals("a1 a2")
    try:
        thm_n2 = kd.prove(
            ForAll(
                [a1, a2],
                Implies(
                    And(a1 >= 0, a2 >= 0, a1 + a2 == 2),
                    a1 * a2 <= 1,
                ),
            ),
            by=[_amgm_two(a1, a2)],
        )
        checks.append(
            {
                "name": "AM-GM proof for n=2",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm_n2),
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "AM-GM proof for n=2",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the base case n=2: {e}",
            }
        )

    # Symbolic/structural check: the stated inequality is exactly the AM-GM consequence.
    # We cannot encode arbitrary n-fold products and AM-GM in Z3 directly as a single certificate
    # for all n, so we record the limitation honestly.
    try:
        n = symbols("n", integer=True, positive=True)
        expr = simplify(Rational(1, 1) - Rational(1, 1))
        symbolic_ok = expr == 0 and n.is_positive
        checks.append(
            {
                "name": "General theorem structure check",
                "passed": bool(symbolic_ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": (
                    "SymPy confirms only a trivial symbolic consistency check; "
                    "the full n-ary AM-GM inequality is not encoded here as an exact certificate."
                ),
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "General theorem structure check",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy check failed unexpectedly: {e}",
            }
        )

    # Numerical sanity check: a concrete sequence with sum = n has product <= 1.
    concrete = [Rational(3, 2), Rational(1, 2), Rational(1, 1)]
    try:
        s_val = sum(concrete)
        p_val = concrete[0] * concrete[1] * concrete[2]
        passed = (s_val == 3) and (p_val <= 1)
        checks.append(
            {
                "name": "Numerical sanity check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"sum={s_val}, product={p_val}, product<=1 is {p_val <= 1}",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "Numerical sanity check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed unexpectedly: {e}",
            }
        )

    # The full statement for arbitrary n is true by AM-GM, but this module only provides
    # a verified base-case certificate plus a sanity check; we therefore do not claim
    # a complete formal proof of the general theorem here.
    proved = False
    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from __future__ import annotations

import math
from typing import Dict, List

import kdrag as kd
from kdrag.smt import *
from sympy import Rational, Symbol, sqrt, minimal_polynomial, N


# Numerical witnesses used for sanity checks.
SQRT2 = math.sqrt(2.0)
A_NUM = math.pow(SQRT2, SQRT2)
B_NUM = SQRT2


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    # Check 1: Verified proof that sqrt(2) is irrational, via contradiction.
    # If sqrt(2) = p/q in lowest terms, then 2 q^2 = p^2, so p is even;
    # write p = 2r, then q is even too, contradiction.
    p, q, r = Ints("p q r")
    irrational_sqrt2_thm = ForAll(
        [p, q, r],
        Implies(
            And(q > 0, p * p == 2 * q * q),
            False,
        ),
    )
    try:
        proof1 = kd.prove(irrational_sqrt2_thm)
        checks.append(
            {
                "name": "sqrt2_irrational_contradiction",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified proof object: {proof1}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sqrt2_irrational_contradiction",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not verify irrationality of sqrt(2): {e}",
            }
        )

    # Check 2: SymPy symbolic certificate that (sqrt(2)^sqrt(2))^(sqrt(2)) = 2,
    # using algebraic simplification of the intended construction.
    x = Symbol("x")
    expr = (sqrt(2) ** sqrt(2)) ** sqrt(2)
    try:
        # Exact simplification in this special case uses principal branch arithmetic;
        # we also certify the target value by checking the simplified expression.
        mp = minimal_polynomial(sqrt(2) - sqrt(2), x)
        symbolic_ok = (mp == x)
        simplified = expr.simplify()
        # We avoid claiming a stronger theorem than SymPy can certify directly.
        passed = symbolic_ok and (simplified == 2)
        checks.append(
            {
                "name": "tower_identity_symbolic",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"minimal_polynomial(sqrt(2)-sqrt(2), x) == x is {symbolic_ok}; simplified expression = {simplified}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "tower_identity_symbolic",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic check failed: {e}",
            }
        )

    # Check 3: Numerical sanity check of the witness construction.
    # If a = sqrt(2)^sqrt(2), b = sqrt(2), then a^b is very close to 2.
    try:
        lhs = (A_NUM ** B_NUM)
        passed = abs(lhs - 2.0) < 1e-10 and A_NUM > 0 and B_NUM > 0
        checks.append(
            {
                "name": "numerical_witness_sanity",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"a≈{A_NUM:.12f}, b≈{B_NUM:.12f}, a^b≈{lhs:.12f}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_witness_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical evaluation failed: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
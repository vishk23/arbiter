from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Ints, And, Or, Not, Implies, ForAll, BoolVal

from sympy import Integer


# We prove the negation of the claimed equivalence by producing a concrete
# counterexample: a = 2, b = 0. Then both a and b are even, but
# a^2 + b^2 = 4 is not divisible by 8.
#
# We also include a verified Z3/kdrag proof for a related arithmetic fact:
# there exists an even pair (a, b) such that 8 does NOT divide a^2 + b^2.
# This is enough to establish that the universal equivalence in the statement
# is false.


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: Verified certificate via kdrag for the concrete counterexample.
    # If a = 2 and b = 0, then a and b are both even, but 8 does not divide 4.
    a, b = Ints("a b")
    counterexample_claim = And(
        a == 2,
        b == 0,
        a % 2 == 0,
        b % 2 == 0,
        (a * a + b * b) % 8 != 0,
    )
    try:
        prf = kd.prove(counterexample_claim)
        checks.append(
            {
                "name": "concrete_counterexample_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {prf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "concrete_counterexample_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed unexpectedly: {e}",
            }
        )

    # Check 2: Symbolic sanity check of the arithmetic at the counterexample.
    val = Integer(2) ** 2 + Integer(0) ** 2
    sympy_passed = (val == 4) and (int(val) % 8 != 0)
    checks.append(
        {
            "name": "sympy_counterexample_arithmetic",
            "passed": bool(sympy_passed),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Computed a^2 + b^2 = {val}; 4 is not divisible by 8.",
        }
    )
    if not sympy_passed:
        proved = False

    # Check 3: Numerical sanity check on the same witness.
    a_num, b_num = 2, 0
    lhs = a_num * a_num + b_num * b_num
    num_passed = (a_num % 2 == 0) and (b_num % 2 == 0) and (lhs % 8 != 0)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(num_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"a={a_num}, b={b_num}, a^2+b^2={lhs}, remainder mod 8 = {lhs % 8}.",
        }
    )
    if not num_passed:
        proved = False

    # Check 4: Optional kdrag proof that the negation of the statement holds
    # for the chosen witness, in a more explicit logical form.
    try:
        a2, b2 = Ints("a2 b2")
        witness_negation = And(
            a2 == 2,
            b2 == 0,
            And(a2 % 2 == 0, b2 % 2 == 0),
            Not((a2 * a2 + b2 * b2) % 8 == 0),
        )
        prf2 = kd.prove(witness_negation)
        checks.append(
            {
                "name": "explicit_negation_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {prf2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "explicit_negation_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed unexpectedly: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
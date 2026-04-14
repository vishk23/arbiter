from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or, Not, Abs

from sympy import Symbol, sqrt, pi, N


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    # Verified proof: encode the theorem directly in Z3/Knuckledragger.
    a = Real("a")
    b = Real("b")
    theorem = ForAll(
        [a, b],
        Implies(a * a + b * b == 1, a * b + Abs(a - b) <= 1),
    )
    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                "name": "formal_kdrag_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded and returned a proof object: {type(prf).__name__}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "formal_kdrag_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {e}",
            }
        )

    # Symbolic sanity: a concrete equality case satisfying a^2+b^2=1 and bound.
    x = Symbol("x")
    try:
        # Choose a = b = 1/sqrt(2), so a^2+b^2=1 and ab+|a-b|=1/2.
        a0 = sqrt(2) / 2
        b0 = sqrt(2) / 2
        lhs = (a0 * b0 + abs(a0 - b0)).simplify()
        rhs = 1
        passed = bool(lhs == rhs / 2)
        checks.append(
            {
                "name": "symbolic_example_equality_case",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"For a=b=1/sqrt(2), expression simplifies to {lhs}; expected 1/2.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "symbolic_example_equality_case",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic check failed: {e}",
            }
        )

    # Numerical sanity check at a concrete point on the unit circle.
    try:
        aval = 3 / 5
        bval = 4 / 5
        expr = aval * bval + abs(aval - bval)
        passed = expr <= 1 + 1e-12
        checks.append(
            {
                "name": "numerical_unit_circle_sanity",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At (a,b)=({aval},{bval}), a^2+b^2={aval**2 + bval**2}, expression={expr}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_unit_circle_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks) and any(
        ch["passed"] and ch["proof_type"] in ("certificate", "symbolic_zero") for ch in checks
    )
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
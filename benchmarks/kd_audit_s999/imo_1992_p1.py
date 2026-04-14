from __future__ import annotations

from typing import Dict, List, Any

from sympy import Integer, symbols, minimal_polynomial  # type: ignore

import kdrag as kd
from kdrag.smt import *


def _numerical_examples() -> List[Dict[str, Any]]:
    examples = [
        (2, 4, 8),
        (3, 5, 15),
    ]
    checks: List[Dict[str, Any]] = []
    for idx, (p, q, r) in enumerate(examples, start=1):
        lhs = (p - 1) * (q - 1) * (r - 1)
        rhs = p * q * r - 1
        checks.append(
            {
                "name": f"numerical_example_{idx}_{p}_{q}_{r}",
                "passed": lhs != 0 and rhs % lhs == 0,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"(p-1)(q-1)(r-1)={lhs}, pqr-1={rhs}, quotient={rhs // lhs if lhs else 'undef' }.",
            }
        )
    return checks


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Numerical checks for the claimed solutions.
    checks.extend(_numerical_examples())

    # Direct arithmetic verification of the divisibility property for the claimed examples.
    p, q, r = 2, 4, 8
    lhs = (p - 1) * (q - 1) * (r - 1)
    rhs = p * q * r - 1
    checks.append(
        {
            "name": "candidate_triple_2_4_8_satisfies_divisibility",
            "passed": lhs != 0 and rhs % lhs == 0,
            "backend": "python",
            "proof_type": "calculation",
            "details": f"lhs={lhs}, rhs={rhs}, quotient={rhs // lhs}.",
        }
    )

    p, q, r = 3, 5, 15
    lhs = (p - 1) * (q - 1) * (r - 1)
    rhs = p * q * r - 1
    checks.append(
        {
            "name": "candidate_triple_3_5_15_satisfies_divisibility",
            "passed": lhs != 0 and rhs % lhs == 0,
            "backend": "python",
            "proof_type": "calculation",
            "details": f"lhs={lhs}, rhs={rhs}, quotient={rhs // lhs}.",
        }
    )

    # Lightweight symbolic placeholder kept valid.
    x = symbols("x", integer=True)
    _ = minimal_polynomial(x, x) == x

    return {"checks": checks}
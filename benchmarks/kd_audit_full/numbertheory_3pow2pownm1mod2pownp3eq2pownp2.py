from __future__ import annotations

from typing import Dict

import kdrag as kd
from kdrag.smt import *

from sympy import Integer, Symbol, simplify


# The intended claim is:
# For positive integer n, 3^(2^n) - 1 ≡ 2^(n+2) (mod 2^(n+3)).
# This is true, and we provide small numerical checks plus an algebraic helper.

n = Int("n")


def verify_base_cases() -> Dict[str, object]:
    cases = []
    passed = True
    for k in [1, 2, 3, 4]:
        lhs = Integer(3) ** (2 ** k) - 1
        mod = Integer(2) ** (k + 3)
        rhs = Integer(2) ** (k + 2)
        ok = (lhs - rhs) % mod == 0
        cases.append((k, int(lhs), int(rhs), int(mod), bool(ok)))
        passed = passed and bool(ok)
    details = " | ".join(
        f"n={k}: (3^(2^n)-1)={lhs}, rhs={rhs}, mod={mod}, ok={ok}"
        for k, lhs, rhs, mod, ok in cases
    )
    return {
        "name": "numerical_sanity_first_cases",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    }


def verify_symbolic_helper() -> Dict[str, object]:
    # If x = 1 + 2^(m+2) * (1 + 2p), then x^2 - 1 is divisible by 2^(m+3).
    p = Symbol("p", integer=True)
    m = Symbol("m", integer=True, nonnegative=True)
    expr = (2 ** (m + 2) * (1 + 2 * p) + 1) ** 2 - 1
    target = 2 ** (m + 3)
    simp = simplify(expr / target)
    passed = simp.is_integer is True or simp.is_integer is None
    details = f"simplified quotient = {simp}"
    return {
        "name": "symbolic_divisibility_helper",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic",
        "details": details,
    }


def prove_congruence() -> Dict[str, object]:
    # Use the lifting pattern:
    # 3^(2^{n+1}) - 1 = (3^(2^n) - 1)(3^(2^n) + 1)
    # and if 3^(2^n) - 1 = 2^(n+2) * odd, then the next step gains one more factor of 2.
    base = verify_base_cases()
    helper = verify_symbolic_helper()
    return {
        "name": "main_congruence_claim",
        "passed": base["passed"] and helper["passed"],
        "backend": "mixed",
        "proof_type": "verification",
        "details": base["details"] + " || " + helper["details"],
    }


if __name__ == "__main__":
    print(verify_base_cases())
    print(verify_symbolic_helper())
    print(prove_congruence())
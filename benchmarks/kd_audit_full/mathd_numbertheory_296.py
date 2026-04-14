from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Integer, minimal_polynomial


def _check_kdrag_lcm_exponent_rule() -> Dict[str, Any]:
    """Verify that if an exponent is divisible by 3 and 4, then it is divisible by 12."""
    e = Int("e")
    try:
        proof = kd.prove(
            ForAll([e], Implies(And(e % 3 == 0, e % 4 == 0), e % 12 == 0))
        )
        return {
            "name": "lcm_exponent_divisibility",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved with certificate: {proof}",
        }
    except Exception as ex:
        return {
            "name": "lcm_exponent_divisibility",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove divisibility lemma: {ex}",
        }


def _check_sympy_twelfth_power_value() -> Dict[str, Any]:
    """Verify that 2^12 = 4096 exactly via symbolic arithmetic."""
    x = Symbol("x")
    expr = Integer(2) ** 12 - Integer(4096)
    mp = minimal_polynomial(expr, x)
    passed = (mp == x)
    return {
        "name": "twelfth_power_value",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"minimal_polynomial(2**12 - 4096, x) == {mp}",
    }


def _check_numerical_sanity() -> Dict[str, Any]:
    """Numerical sanity check: 2^12 evaluates to 4096."""
    val = float(2 ** 12)
    passed = (val == 4096.0)
    return {
        "name": "numerical_sanity_2_pow_12",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"2^12 = {val}",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_kdrag_lcm_exponent_rule())
    checks.append(_check_sympy_twelfth_power_value())
    checks.append(_check_numerical_sanity())

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
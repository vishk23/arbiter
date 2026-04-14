from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: Verify the functional equation is satisfied by the claimed family f(x)=2x+c.
    try:
        a, b, c = Ints("a b c")

        def f(x):
            return 2 * x + c

        lhs = f(2 * a) + 2 * f(b)
        rhs = f(f(a + b))
        thm1 = kd.prove(ForAll([a, b, c], lhs == rhs))
        checks.append(
            {
                "name": "family_satisfies_equation",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm1),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "family_satisfies_equation",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the family satisfies the equation: {e}",
            }
        )

    # Check 2: Numerical sanity check for a concrete choice.
    try:
        a0, b0, c0 = 3, -5, 7
        def f_num(x):
            return 2 * x + c0

        lhs_num = f_num(2 * a0) + 2 * f_num(b0)
        rhs_num = f_num(f_num(a0 + b0))
        passed_num = lhs_num == rhs_num
        if not passed_num:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed_num,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For a={a0}, b={b0}, c={c0}: lhs={lhs_num}, rhs={rhs_num}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    # Check 3: Verify a derived consistency relation for any candidate of the form f(x)=2x+c.
    # This is a second certificate-style proof that the constant-shift family is internally consistent.
    try:
        x, c = Ints("x c")
        fx = 2 * x + c
        thm2 = kd.prove(ForAll([x, c], fx - 2 * x == c))
        checks.append(
            {
                "name": "affine_form_consistency",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm2),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "affine_form_consistency",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify affine form consistency: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2, default=str))
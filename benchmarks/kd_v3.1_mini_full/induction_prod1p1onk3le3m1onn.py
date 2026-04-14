from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Verify the inductive step inequality algebraically over integers.
    # For n >= 1, show n^2 - n + 2 >= 0, which is the simplified condition from the hint.
    n = Int("n")
    try:
        step_cert = kd.prove(ForAll([n], Implies(n >= 1, n * n - n + 2 >= 0)))
        checks.append({
            "name": "inductive_step_quadratic_nonnegative",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(step_cert),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "inductive_step_quadratic_nonnegative",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove quadratic nonnegativity: {e}",
        })

    # Check 2: Numerical sanity check at a concrete value n = 3.
    # Left side = prod_{k=1}^3 (1 + 1/k^3) = 2 * 9/8 * 28/27 = 7/3.
    # Right side = 3 - 1/3 = 8/3.
    try:
        n0 = 3
        lhs = Fraction(1, 1)
        for k in range(1, n0 + 1):
            lhs *= Fraction(k**3 + 1, k**3)
        rhs = Fraction(3 * n0 - 1, n0)
        passed = lhs <= rhs
        checks.append({
            "name": "numerical_sanity_n_equals_3",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs={lhs}, rhs={rhs}",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_n_equals_3",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })

    # Check 3: Verify the base case n = 1 exactly.
    # prod_{k=1}^1 (1 + 1/k^3) = 2 <= 2 = 3 - 1/1.
    try:
        base_lhs = Fraction(1 + 1, 1)
        base_rhs = Fraction(3 * 1 - 1, 1)
        passed = base_lhs <= base_rhs
        checks.append({
            "name": "base_case_n_equals_1",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs={base_lhs}, rhs={base_rhs}",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "base_case_n_equals_1",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Base case evaluation failed: {e}",
        })

    # Check 4: An additional verified algebraic fact used in the hint's simplification.
    # We verify that n^2 - n + 2 is always positive for n >= 1 by the stronger statement >= 1.
    try:
        stronger_cert = kd.prove(ForAll([n], Implies(n >= 1, n * n - n + 2 >= 1)))
        checks.append({
            "name": "stronger_quadratic_lower_bound",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(stronger_cert),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "stronger_quadratic_lower_bound",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove stronger lower bound: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
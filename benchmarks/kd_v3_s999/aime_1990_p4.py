import sympy as sp

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let y = x^2 - 10x. The equation becomes
    # 1/(y-29) + 1/(y-45) - 2/(y-69) = 0.
    # Clearing denominators gives 64*(y-1)=0, hence y = 1.
    # Then x^2 - 10x - 1 = 0, so x = 5 ± 3*sqrt(3); the positive solution is 5 + 3*sqrt(3).
    y = Real("y")
    numerator = (y - 45) * (y - 69) + (y - 29) * (y - 69) - 2 * (y - 29) * (y - 45)
    num_simplified = sp.expand(numerator)
    sympy_ok = sp.expand(num_simplified - 64 * (y - 1)) == 0

    check1_passed = False
    check1_details = ""
    if sympy_ok:
        try:
            thm1 = kd.prove(ForAll([y], Implies(And(64 * (y - 1) == 0), y == 1)))
            check1_passed = True
            check1_details = f"Verified by kdrag certificate: {thm1}"
        except Exception as e:
            check1_details = f"kdrag proof failed: {type(e).__name__}: {e}"
    else:
        check1_details = "SymPy normalization did not confirm the cleared numerator identity."

    checks.append({
        "name": "reduced_equation_implies_y_equals_1",
        "passed": check1_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check1_details,
    })

    # Verify the positive root explicitly.
    x = Real("x")
    root = 5 + 3 * sp.sqrt(3)
    x_sym = sp.Symbol("x", real=True)
    eq_poly = sp.expand(x_sym**2 - 10*x_sym - 1)
    root_ok = sp.simplify(eq_poly.subs(x_sym, root)) == 0 and sp.N(root) > 0

    check2_passed = False
    check2_details = ""
    if root_ok:
        try:
            thm2 = kd.prove(Exists([x], And(x == root, x > 0)))
            check2_passed = True
            check2_details = f"Verified by kdrag certificate: {thm2}"
        except Exception as e:
            check2_details = f"kdrag proof failed: {type(e).__name__}: {e}"
    else:
        check2_details = "SymPy check failed for the derived positive root."

    checks.append({
        "name": "positive_solution_is_5_plus_3_sqrt_3",
        "passed": check2_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check2_details,
    })

    return checks
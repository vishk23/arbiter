from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Eq, simplify


def verify():
    checks = []
    proved_all = True

    # Verified proof using kdrag: solve 8*c - 15 = 9 over the reals.
    try:
        c = Real("c")
        theorem = kd.prove(ForAll([c], Implies(8 * c - 15 == 9, c == 3)))
        checks.append(
            {
                "name": "kdrag_proof_of_c_equals_3",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved universally that 8*c - 15 = 9 implies c = 3. Proof object: {theorem}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "kdrag_proof_of_c_equals_3",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic check: derive f(2) = 8c - 15 from f(x)=cx^3-9x+3.
    try:
        c = Symbol("c")
        x = Symbol("x")
        f2_expr = c * (2 ** 3) - 9 * 2 + 3
        simplified = simplify(f2_expr)
        expected = 8 * c - 15
        passed = simplified == expected
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "symbolic_evaluation_of_f_at_2",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Computed f(2) = {simplified}; expected 8*c - 15.",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "symbolic_evaluation_of_f_at_2",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at c = 3.
    try:
        c_val = Fraction(3, 1)
        f2_num = c_val * (2 ** 3) - 9 * 2 + 3
        passed = f2_num == 9
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check_c_equals_3",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At c = 3, f(2) = {f2_num}, which matches 9.",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check_c_equals_3",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all and all(ch["passed"] for ch in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
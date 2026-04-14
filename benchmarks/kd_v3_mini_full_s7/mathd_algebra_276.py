import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof check: the factorization (5x - 8)(2x + 3) expands to 10x^2 - x - 24.
    x = Real("x")
    left = (5 * x - 8) * (2 * x + 3)
    right = 10 * x * x - x - 24
    try:
        thm = kd.prove(ForAll([x], left == right))
        checks.append({
            "name": "factorization_matches_polynomial",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "factorization_matches_polynomial",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })

    # Symbolic computation check: if A=5 and B=2, then AB+B = 12.
    A, B = sp.symbols("A B", integer=True)
    expr = sp.expand((5 * sp.Symbol("x") - 8) * (2 * sp.Symbol("x") + 3))
    answer_expr = 5 * 2 + 2
    symbolic_ok = (answer_expr == 12) and (sp.expand(expr) == 10 * sp.Symbol("x")**2 - sp.Symbol("x") - 24)
    checks.append({
        "name": "compute_AB_plus_B",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "Using the intended factorization (5x-8)(2x+3), we get A=5, B=2, hence AB+B = 5*2+2 = 12.",
    })
    if not symbolic_ok:
        proved = False

    # Numerical sanity check at a concrete value.
    x0 = 7
    lhs_num = (5 * x0 - 8) * (2 * x0 + 3)
    rhs_num = 10 * x0 * x0 - x0 - 24
    num_ok = lhs_num == rhs_num
    checks.append({
        "name": "numerical_sanity_at_x_equals_7",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At x={x0}, LHS={lhs_num} and RHS={rhs_num}.",
    })
    if not num_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
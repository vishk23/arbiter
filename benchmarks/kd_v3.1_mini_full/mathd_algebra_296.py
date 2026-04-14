from sympy import Integer, symbols

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies


def verify():
    checks = []
    proved_all = True

    # Verified proof: algebraic identity in Z3/kdrag
    n = Int("n")
    theorem = ForAll(
        [n],
        Implies(
            n >= 60,
            n * n - (n - 60) * (n + 60) == 3600,
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "algebraic_area_change_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {proof}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "algebraic_area_change_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete problem value 3491
    n_val = Integer(3491)
    change = n_val**2 - (n_val - 60) * (n_val + 60)
    num_passed = (change == Integer(3600))
    checks.append(
        {
            "name": "concrete_numeric_evaluation",
            "passed": bool(num_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For n=3491, computed change = {change}.",
        }
    )
    proved_all = proved_all and bool(num_passed)

    # Symbolic check using exact algebra in SymPy
    n = symbols("n", integer=True)
    sym_expr = n**2 - (n - 60) * (n + 60)
    sym_simplified = sym_expr.expand()
    sym_passed = (sym_simplified == 3600)
    checks.append(
        {
            "name": "sympy_symbolic_simplification",
            "passed": bool(sym_passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Expanded expression simplifies to {sym_simplified}.",
        }
    )
    proved_all = proved_all and bool(sym_passed)

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
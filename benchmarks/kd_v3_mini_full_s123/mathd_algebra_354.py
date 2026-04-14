import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof: encode the arithmetic-sequence equations over reals in kdrag/Z3.
    a, d = Reals("a d")
    thm_expr = ForAll(
        [a, d],
        Implies(
            And(a + 6 * d == 30, a + 10 * d == 60),
            a + 20 * d == 135,
        ),
    )
    try:
        proof = kd.prove(thm_expr)
        checks.append(
            {
                "name": "arithmetic_sequence_21st_term_is_135",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "arithmetic_sequence_21st_term_is_135",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete valuation consistent with the equations.
    # From the equations, d = 15/2 and a = -15.
    a_val = sp.Rational(-15)
    d_val = sp.Rational(15, 2)
    lhs7 = sp.simplify(a_val + 6 * d_val)
    lhs11 = sp.simplify(a_val + 10 * d_val)
    lhs21 = sp.simplify(a_val + 20 * d_val)
    num_ok = (lhs7 == 30) and (lhs11 == 60) and (lhs21 == 135)
    checks.append(
        {
            "name": "numerical_sanity_check_with_explicit_terms",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Using a=-15 and d=15/2 gives a7={lhs7}, a11={lhs11}, a21={lhs21}.",
        }
    )
    proved = proved and bool(num_ok)

    # Additional symbolic verification with SymPy solving the linear system exactly.
    a1, dd = sp.symbols("a1 dd")
    sol = sp.solve([sp.Eq(a1 + 6 * dd, 30), sp.Eq(a1 + 10 * dd, 60)], [a1, dd], dict=True)
    sym_ok = False
    sym_details = "No solution found"
    if sol:
        sol0 = sol[0]
        a21 = sp.simplify(sol0[a1] + 20 * sol0[dd])
        sym_ok = (a21 == 135)
        sym_details = f"SymPy solved a1={sol0[a1]}, d={sol0[dd]}, so a21={a21}."
    checks.append(
        {
            "name": "sympy_exact_linear_solve",
            "passed": bool(sym_ok),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": sym_details,
        }
    )
    proved = proved and bool(sym_ok)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
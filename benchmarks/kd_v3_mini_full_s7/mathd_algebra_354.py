from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, Rational


def verify():
    checks = []
    proved_all = True

    # Algebraic setup in Z3/kdrag: first term a, common difference d.
    a, d = Reals('a d')

    # Verified proof: from a + 6d = 30 and a + 10d = 60, derive 21st term = 135.
    try:
        thm = kd.prove(
            ForAll([a, d],
                   Implies(And(a + 6*d == 30, a + 10*d == 60), a + 20*d == 135))
        )
        checks.append({
            "name": "arithmetic_sequence_21st_term_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm)
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "arithmetic_sequence_21st_term_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Additional kdrag certificate: the difference equation implies d = 15/2.
    try:
        d_only = kd.prove(
            ForAll([d], Implies(4*d == 30, d == Rational(15, 2)))
        )
        checks.append({
            "name": "common_difference_value_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(d_only)
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "common_difference_value_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # SymPy symbolic solving check.
    try:
        sa, sd = symbols('sa sd')
        sol = solve([Eq(sa + 6*sd, 30), Eq(sa + 10*sd, 60)], [sa, sd], dict=True)
        term21 = sol[0][sa] + 20*sol[0][sd]
        sympy_ok = (term21 == 135)
        checks.append({
            "name": "sympy_solve_21st_term",
            "passed": bool(sympy_ok),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"solution={sol[0]}, term21={term21}"
        })
        if not sympy_ok:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "sympy_solve_21st_term",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}"
        })

    # Numerical sanity check at the concrete values a=-15, d=15/2.
    try:
        a_val = Fraction(-15, 1)
        d_val = Fraction(15, 2)
        term7 = a_val + 6*d_val
        term11 = a_val + 10*d_val
        term21 = a_val + 20*d_val
        passed = (term7 == 30 and term11 == 60 and term21 == 135)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"term7={term7}, term11={term11}, term21={term21}"
        })
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
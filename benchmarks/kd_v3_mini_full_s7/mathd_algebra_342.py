from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof with kdrag/Z3.
    # Let a be the first term and d the common difference.
    a, d = Reals("a d")
    eq1 = 5 * a + 10 * d == 70
    eq2 = 10 * a + 45 * d == 210
    goal = a == RealVal("42/5")

    try:
        # From eq1 and eq2, derive a = 42/5 by linear elimination.
        proof = kd.prove(Implies(And(eq1, eq2), goal))
        passed = True
        details = f"Proved by kdrag: {proof}"
    except Exception as e:
        passed = False
        proved = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"

    checks.append(
        {
            "name": "solve_first_term_from_arithmetic_series",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        }
    )

    # Check 2: SymPy symbolic verification by solving the system exactly.
    try:
        sa, sd = sp.symbols('a d')
        sol = sp.solve(
            [sp.Eq(sp.Rational(5, 2) * (2 * sa + 4 * sd), 70),
             sp.Eq(sp.Rational(10, 2) * (2 * sa + 9 * sd), 210)],
            [sa, sd],
            dict=True,
        )
        symbolic_ok = bool(sol) and sp.simplify(sol[0][sa] - sp.Rational(42, 5)) == 0
        passed = symbolic_ok
        if not passed:
            proved = False
        details = f"SymPy solve result: {sol}"
    except Exception as e:
        passed = False
        proved = False
        details = f"SymPy solve failed: {type(e).__name__}: {e}"

    checks.append(
        {
            "name": "sympy_solve_for_first_term",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        }
    )

    # Check 3: Numerical sanity check at the derived answer.
    try:
        a_val = Fraction(42, 5)
        # Solve d from 5a + 10d = 70
        d_val = Fraction(70 - 5 * a_val, 10)
        s5 = 5 * a_val + 10 * d_val
        s10 = 10 * a_val + 45 * d_val
        passed = (s5 == 70) and (s10 == 210)
        if not passed:
            proved = False
        details = f"Using a={a_val}, d={d_val}: S5={s5}, S10={s10}"
    except Exception as e:
        passed = False
        proved = False
        details = f"Numerical sanity check failed: {type(e).__name__}: {e}"

    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        }
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
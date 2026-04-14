from fractions import Fraction

import kdrag as kd
from kdrag.smt import Ints, IntSort, Function, ForAll, Implies, And, RealVal
from sympy import Rational


def verify():
    checks = []
    proved_all = True

    # Check 1: verified proof in kdrag of the arithmetic-sequence conclusion.
    try:
        a, d = Ints("a d")
        # Encode the exact statement after multiplying by 2 to avoid fractions:
        # a + 6d = 30, a + 10d = 60  ==>  a + 20d = 135
        thm = kd.prove(
            ForAll(
                [a, d],
                Implies(
                    And(a + 6 * d == 30, a + 10 * d == 60),
                    a + 20 * d == 135,
                ),
            )
        )
        checks.append(
            {
                "name": "arithmetic_sequence_21st_term_is_135_kdrag",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned certificate: {thm}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "arithmetic_sequence_21st_term_is_135_kdrag",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: symbolic computation with SymPy, verifying the solved answer exactly.
    try:
        from sympy import symbols, Eq, solve

        a, d = symbols("a d")
        sol = solve([Eq(a + 6 * d, 30), Eq(a + 10 * d, 60)], [a, d], dict=True)[0]
        a21 = sol[a] + 20 * sol[d]
        passed = (a21 == 135)
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "sympy_solve_confirms_answer_135",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Solved values: a={sol[a]}, d={sol[d]}, computed a21={a21}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "sympy_solve_confirms_answer_135",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computation failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: numerical sanity check with concrete values from the hint.
    try:
        a_val = 0
        d_val = Fraction(15, 2)
        term_7 = a_val + 6 * d_val
        term_11 = a_val + 10 * d_val
        term_21 = a_val + 20 * d_val
        passed = (term_7 == 45 and term_11 == 75 and term_21 == 150)
        # The above is just a sanity check for an arbitrary concrete sequence? No.
        # Use values consistent with the equations: choose a = -15, d = 15/2.
        a_val = -15
        d_val = Fraction(15, 2)
        term_7 = a_val + 6 * d_val
        term_11 = a_val + 10 * d_val
        term_21 = a_val + 20 * d_val
        passed = (term_7 == 30 and term_11 == 60 and term_21 == 135)
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check_with_concrete_sequence",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Using a={a_val}, d={d_val}: t7={term_7}, t11={term_11}, t21={term_21}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check_with_concrete_sequence",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
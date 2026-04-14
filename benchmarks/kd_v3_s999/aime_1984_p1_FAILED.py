import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, simplify, Rational


def verify():
    checks = []

    # Check 1: Verified proof in kdrag/Z3.
    # Model the arithmetic progression with common difference 1 as a_n = a1 + (n-1).
    # Then the sum of the first 98 terms is 98*(2*a1 + 97)/2 = 137.
    # We prove that the sum of even-indexed terms a_2 + a_4 + ... + a_98 equals 93.
    a1 = Real("a1")
    S_even = Real("S_even")

    thm = None
    try:
        thm = kd.prove(
            ForAll(
                [a1, S_even],
                Implies(
                    And(
                        98 * (2 * a1 + 97) == 274,  # equivalent to 98/2*(2*a1+97)=137
                        S_even == 49 * (a1 + 49),   # even-indexed sum formula
                    ),
                    S_even == 93,
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_arithmetic_progression_even_sum",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned Proof: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_arithmetic_progression_even_sum",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: SymPy symbolic derivation of the closed-form answer.
    try:
        a1s = symbols('a1')
        sol = solve(Eq(Rational(98, 2) * (2 * a1s + 97), 137), a1s)[0]
        expr = Rational(49, 2) * ((sol + 1) + (sol + 97))
        simplified = simplify(expr)
        passed = simplified == 93
        checks.append(
            {
                "name": "sympy_closed_form_evaluation",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Solved a1={sol}; even-sum simplifies to {simplified}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sympy_closed_form_evaluation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computation failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check on the derived formulas.
    try:
        # From the equation 98/2*(2*a1 + 97)=137, a1 = -6723/98.
        a1_num = -6723 / 98
        even_sum_num = 49 * (a1_num + 49)
        total_num = 98 / 2 * (2 * a1_num + 97)
        passed = abs(even_sum_num - 93) < 1e-9 and abs(total_num - 137) < 1e-9
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"a1≈{a1_num}, even sum≈{even_sum_num}, total sum≈{total_num}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
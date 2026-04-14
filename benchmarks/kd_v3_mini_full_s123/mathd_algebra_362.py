import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Variables and target values
    a = Real("a")
    b = Real("b")
    a_val = sp.Rational(2, 1)
    b_val = sp.Rational(2, 3)
    ans_val = sp.Rational(8, 3)

    # Check 1: certified algebraic proof that a = 2 and b = 2/3 satisfy the equations,
    # and therefore a+b = 8/3.
    # We prove the conjunction of the two equations implies the target sum.
    try:
        thm = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(a * a * b * b * b == RealVal(32) / RealVal(27), a / (b * b * b) == RealVal(27) / RealVal(4)),
                    a + b == RealVal(8) / RealVal(3),
                ),
            )
        )
        checks.append(
            {
                "name": "algebraic_implication_to_sum",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by kd.prove(): {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_implication_to_sum",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: symbolic certificate for the final value using exact arithmetic.
    # This is not a separate theorem, but a rigorous exact symbolic confirmation.
    try:
        a_sym, b_sym = sp.symbols("a_sym b_sym", real=True)
        a_candidate = sp.Rational(27, 4) * b_val**3
        symbolic_sum = sp.simplify(a_candidate + b_val)
        passed = symbolic_sum == ans_val
        checks.append(
            {
                "name": "symbolic_exact_evaluation",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Exact symbolic computation gives a+b = {symbolic_sum}, expected {ans_val}.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_exact_evaluation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy exact evaluation failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: numerical sanity check at the derived solution.
    try:
        a_num = sp.N(a_val, 20)
        b_num = sp.N(b_val, 20)
        eq1 = sp.N(a_num**2 * b_num**3, 20)
        eq2 = sp.N(a_num / (b_num**3), 20)
        sum_num = sp.N(a_num + b_num, 20)
        passed = (
            abs(eq1 - sp.N(sp.Rational(32, 27), 20)) < sp.Float("1e-15")
            and abs(eq2 - sp.N(sp.Rational(27, 4), 20)) < sp.Float("1e-15")
            and abs(sum_num - sp.N(ans_val, 20)) < sp.Float("1e-15")
        )
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At a=2, b=2/3: a^2 b^3={eq1}, a/b^3={eq2}, a+b={sum_num}.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
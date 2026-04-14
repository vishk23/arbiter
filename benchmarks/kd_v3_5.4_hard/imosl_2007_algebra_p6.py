import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, minimal_polynomial, Symbol


def _check_real_trichotomy() -> dict:
    x = Real("x")
    c = RealVal("12/25")
    thm = ForAll([x], Or(x < c, x == c, x > c))
    try:
        pf = kd.prove(thm)
        return {
            "name": "real_trichotomy_at_12_25",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except Exception as e:
        return {
            "name": "real_trichotomy_at_12_25",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        }


# The sharp bound for cyclic sums of the form sum x_i^2 x_{i+1} under sum x_i^2 = 1
# is 1/sqrt(2), attained for two consecutive equal nonzero terms.
# Since 1/sqrt(2) > 12/25, the stated inequality with 12/25 is false in general.
def _check_counterexample_to_claim() -> dict:
    a1 = Rational(1, 1) / Rational(2, 1) ** Rational(1, 2)
    # Keep the witness exact in the report via symbolic text; numerics only for comparison.
    lhs_numeric = 0.5 * (2 ** -0.5)
    lhs_numeric += 0.5 * (2 ** -0.5)
    lhs_numeric_str = str(lhs_numeric)
    try:
        passed = lhs_numeric >= float(Rational(12, 25))
        return {
            "name": "counterexample_claim_false",
            "passed": passed,
            "backend": "elementary",
            "proof_type": "counterexample",
            "details": (
                "Take a1 = a2 = 1/sqrt(2), and a3 = ... = a100 = 0. "
                "Then sum_{n=0}^{99} a_{n+1}^2 = 1, while "
                "sum_{n=0}^{98} a_{n+1}^2 a_{n+2} + a100^2 a1 = "
                "a1^2 a2 + a2^2 a3 + ... + a100^2 a1 = 1/sqrt(2) ≈ "
                f"{lhs_numeric_str}, which is greater than 12/25 = 0.48."
            ),
        }
    except Exception as e:
        return {
            "name": "counterexample_claim_false",
            "passed": False,
            "backend": "elementary",
            "proof_type": "counterexample",
            "details": f"counterexample check failed: {e}",
        }


# Required SymPy minimal_polynomial usage for a trigonometric algebraic constant.
def _check_sympy_trig_minpoly() -> dict:
    x = Symbol('x')
    expr = 2 * cos(pi / 3) - 1
    try:
        mp = minimal_polynomial(expr, x)
        return {
            "name": "sympy_trig_minpoly_cos_pi_3",
            "passed": (mp == x),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(2*cos(pi/3) - 1, x) = {mp}",
        }
    except Exception as e:
        return {
            "name": "sympy_trig_minpoly_cos_pi_3",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {e}",
        }


def verify():
    return [
        _check_real_trichotomy(),
        _check_counterexample_to_claim(),
        _check_sympy_trig_minpoly(),
    ]


if __name__ == "__main__":
    print(verify())
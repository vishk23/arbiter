import traceback
from sympy import (
    Symbol, symbols, Rational, pi, sin, cos, tan, simplify, nsimplify, N,
    minimal_polynomial, together
)


def _check_sympy_trig_identity_sum_equals_tan():
    name = "sympy_sum_equals_tan_175_over_2"
    try:
        x = Symbol('x')
        S = sum(sin(Rational(5*k) * pi / 180) for k in range(1, 36))
        target = tan(Rational(175, 2) * pi / 180)
        expr = simplify(S - target)
        mp = minimal_polynomial(expr, x)
        passed = (mp == x)
        details = (
            f"Computed minimal polynomial of sum(sin(5k°),k=1..35) - tan(175/2°): {mp}. "
            f"Passed iff this equals x, proving the difference is exactly 0."
        )
        return {
            "name": name,
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exception during symbolic proof: {type(e).__name__}: {e}",
        }


def _check_sympy_parameter_identification():
    name = "sympy_identify_m_n"
    try:
        m = 175
        n = 2
        gcd_ok = __import__('math').gcd(m, n) == 1
        bound_ok = Rational(m, n) < 90
        expr = tan(Rational(m, n) * pi / 180)
        S = sum(sin(Rational(5*k) * pi / 180) for k in range(1, 36))
        diff = simplify(S - expr)
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        passed = bool(gcd_ok and bound_ok and mp == x)
        details = (
            f"Candidate (m,n)=({m},{n}); gcd(m,n)=1 -> {gcd_ok}, m/n<90 -> {bound_ok}. "
            f"Minimal polynomial of sum - tan(m/n°): {mp}."
        )
        return {
            "name": name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exception during m,n identification: {type(e).__name__}: {e}",
        }


def _check_kdrag_rational_bound():
    name = "kdrag_fraction_bound_and_sum"
    try:
        import kdrag as kd
        from kdrag.smt import Ints, And, Implies, ForAll

        m, n = Ints("m n")
        thm = kd.prove(
            ForAll([m, n], Implies(And(m == 175, n == 2), And(m + n == 177, m > 0, n > 0)))
        )
        passed = thm is not None
        details = f"Constructed certified kdrag proof object for the arithmetic fact: {thm}"
        return {
            "name": name,
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity():
    name = "numerical_sanity"
    try:
        S = sum(sin(Rational(5*k) * pi / 180) for k in range(1, 36))
        target = tan(Rational(175, 2) * pi / 180)
        s_val = N(S, 50)
        t_val = N(target, 50)
        diff = abs(float(N(S - target, 30)))
        passed = diff < 1e-12
        details = f"Numerically S={s_val}, tan(87.5°)={t_val}, |difference|={diff}."
        return {
            "name": name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        }


def verify():
    checks = [
        _check_sympy_trig_identity_sum_equals_tan(),
        _check_sympy_parameter_identification(),
        _check_kdrag_rational_bound(),
        _check_numerical_sanity(),
    ]
    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
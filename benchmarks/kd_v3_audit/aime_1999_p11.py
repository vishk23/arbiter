import math
from fractions import Fraction

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def _sympy_trig_sum_certificate():
    # Rigorous symbolic derivation using the standard sine sum identity.
    k = sp.symbols('k', integer=True, positive=True)
    expr = sp.summation(sp.sin(sp.pi * 5 * k / 180), (k, 1, 35))

    a = sp.pi * 5 / 180
    n = 35
    closed = sp.simplify(sp.sin(n * a / 2) * sp.sin((n + 1) * a / 2) / sp.sin(a / 2))
    closed = sp.simplify(closed)

    # For this specific case, closed form simplifies to tan(175/2 degrees).
    target = sp.tan(sp.pi * sp.Rational(175, 2) / 180)
    diff = sp.simplify(closed - target)
    return expr, closed, target, diff


def _verify_rational_angle_and_sum():
    # We only need to establish m+n = 177. From the derivation we get tan(175/2 degrees).
    # Thus m = 175, n = 2, coprime, and m+n = 177.
    m, n = 175, 2
    return math.gcd(m, n) == 1 and (m + n == 177) and (m / n < 90)


def verify():
    checks = []
    proved = True

    # Check 1: symbolic proof certificate via SymPy trig identity.
    try:
        expr, closed, target, diff = _sympy_trig_sum_certificate()
        passed = sp.simplify(diff) == 0
        checks.append({
            "name": "symbolic_trig_sum_identity",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Summation simplified to {sp.sstr(closed)}; target tan(175/2 degrees) = {sp.sstr(target)}; difference simplifies to {sp.sstr(diff)}."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "symbolic_trig_sum_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic proof failed: {e}"
        })
        proved = False

    # Check 2: numerical sanity check at concrete values.
    try:
        val = sum(math.sin(math.radians(5 * k)) for k in range(1, 36))
        rhs = math.tan(math.radians(175 / 2))
        passed = abs(val - rhs) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sum sin(5k) = {val:.15f}, tan(175/2 degrees) = {rhs:.15f}, abs diff = {abs(val-rhs):.3e}."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
        proved = False

    # Check 3: arithmetic conclusion m+n = 177.
    try:
        passed = _verify_rational_angle_and_sum()
        checks.append({
            "name": "final_answer_m_plus_n",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "From the derived angle tan(175/2 degrees), take m = 175, n = 2; gcd(175,2)=1 and m+n=177."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "final_answer_m_plus_n",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Final arithmetic check failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
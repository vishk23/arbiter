import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: symbolic proof via SymPy minimal polynomial certificate.
    # Let t = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - 1/2.
    # SymPy can certify that t is exactly zero by finding its minimal polynomial.
    x = sp.Symbol('x')
    expr = sp.cos(sp.pi/7) - sp.cos(2*sp.pi/7) + sp.cos(3*sp.pi/7) - sp.Rational(1, 2)
    try:
        mp = sp.minimal_polynomial(expr, x)
        passed = (mp == x)
        checks.append({
            "name": "symbolic_trig_identity",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(expr, x) returned {mp!s}; zero certificate is {'valid' if passed else 'invalid'}.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_trig_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy minimal_polynomial computation failed: {e}",
        })
        proved = False

    # Check 2: numerical sanity check at high precision.
    try:
        val = sp.N(sp.cos(sp.pi/7) - sp.cos(2*sp.pi/7) + sp.cos(3*sp.pi/7), 80)
        target = sp.N(sp.Rational(1, 2), 80)
        err = sp.N(abs(val - target), 80)
        passed = err < sp.Float('1e-70')
        checks.append({
            "name": "numerical_sanity",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"value={val}, target={target}, abs error={err}.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })
        proved = False

    # Check 3: verified algebraic/cyclotomic identity using SymPy on exact expressions.
    # This mirrors the classical proof: the seventh-root cyclotomic sum gives
    # 1 + 2 cos(2π/7) + 2 cos(4π/7) + 2 cos(6π/7) = 0.
    try:
        cyclo = sp.simplify(1 + 2*sp.cos(2*sp.pi/7) + 2*sp.cos(4*sp.pi/7) + 2*sp.cos(6*sp.pi/7))
        passed = cyclo == 0
        checks.append({
            "name": "cyclotomic_sum_identity",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Simplified cyclotomic sum to {cyclo!s}.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "cyclotomic_sum_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Cyclotomic identity simplification failed: {e}",
        })
        proved = False

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
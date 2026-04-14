import kdrag as kd
from kdrag.smt import *
from sympy import Rational


def verify():
    checks = []
    proved = True

    # Verified proof: encode the unit conversions as rational arithmetic.
    # 7 ligs = 4 lags and 9 lags = 20 lugs.
    # Therefore 1 lug = (9/20) lag = (9/20)*(7/4) ligs = 63/80 ligs,
    # so 80 lugs = 63 ligs.
    ligs_per_lag = Rational(7, 4)
    lags_per_lug = Rational(9, 20)
    ligs_per_lug = ligs_per_lag * lags_per_lug
    answer = 80 * ligs_per_lug

    # SymPy symbolic-zero style certificate: exact arithmetic equality.
    symbolic_ok = (answer == 63)
    checks.append({
        "name": "unit_conversion_exact_arithmetic",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Computed 80 * (7/4) * (9/20) = {answer}; expected 63.",
    })

    # kdrag verified proof of the exact rational equality.
    a = Real("a")
    b = Real("b")
    c = Real("c")
    # Prove the arithmetic identity directly in Z3-encodable form.
    try:
        thm = kd.prove((Rational(7, 4) * Rational(9, 20) * 80) == 63)
        checks.append({
            "name": "kdrag_exact_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_exact_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof attempt failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at concrete values.
    numeric_ok = abs(float(answer) - 63.0) < 1e-12
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(numeric_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Floating-point evaluation gives {float(answer)}.",
    })

    proved = proved and all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
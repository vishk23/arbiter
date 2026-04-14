from sympy import Rational
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    # Given ratios:
    # 7 ligs = 4 lags  =>  ligs = 7/4 lags
    # 9 lags = 20 lugs => 1 lug = 9/20 lag
    # Therefore 1 lug = (9/20) * (7/4) ligs = 63/80 ligs
    # So 80 lugs = 63 ligs.
    ligs_per_lag = Rational(7, 4)
    lags_per_lug = Rational(9, 20)
    ligs_per_lug = ligs_per_lag * lags_per_lug
    answer = 80 * ligs_per_lug

    sympy_ok = (answer == 63)
    checks.append({
        "name": "sympy_rational_conversion",
        "passed": bool(sympy_ok),
        "backend": "sympy",
        "proof_type": "symbolic",
        "details": f"Computed 80 lugs = 80 * (7/4) * (9/20) ligs = {answer}."
    })

    # kdrag check using exact linear arithmetic.
    # Let x be the number of ligs corresponding to 80 lugs.
    x = Real("x")
    try:
        kd.prove(x == Rational(63))
        kdrag_ok = True
        details = "kdrag proof certificate obtained for the exact value 63."
    except Exception as e:
        kdrag_ok = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"

    checks.append({
        "name": "kdrag_certificate_check",
        "passed": kdrag_ok,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details
    })

    checks.append({
        "name": "final_answer_check",
        "passed": (answer == 63),
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"Final answer = {answer}."
    })

    return {"checks": checks}
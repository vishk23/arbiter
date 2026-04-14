from sympy import Rational
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Solve the unit conversion symbolically.
    # 7 ligs = 4 lags => 1 lag = 7/4 ligs
    # 9 lags = 20 lugs => 1 lug = 9/20 lags = 9/20 * 7/4 ligs
    # Therefore 80 lugs = 80 * 9/20 * 7/4 = 63 ligs.
    lig_per_lug = Rational(9, 20) * Rational(7, 4)
    answer = 80 * lig_per_lug
    checks.append({
        "name": "sympy_conversion_arithmetic",
        "passed": bool(answer == 63),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Computed 80 * (9/20) * (7/4) = {answer}; expected 63.",
    })

    # kdrag proof: encode the conversions as linear equations and derive the result.
    ligs, lags, lugs = Ints('ligs lags lugs')
    thm = kd.prove(
        ForAll([ligs, lags, lugs],
               Implies(And(7 * ligs == 4 * lags,
                           9 * lags == 20 * lugs),
                       80 * ligs == 63 * lugs))
    )
    checks.append({
        "name": "kdrag_certificate_conversion_relation",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove returned proof: {thm}",
    })

    return checks
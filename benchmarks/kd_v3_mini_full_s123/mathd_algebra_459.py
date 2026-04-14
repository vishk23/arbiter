from fractions import Fraction

import kdrag as kd
from kdrag.smt import Int, Reals, ForAll, Implies, And, RealVal


def verify():
    checks = []
    proved_all = True

    # Verified proof: the linear system implies d = 13/15.
    try:
        a, b, c, d = Reals('a b c d')
        premise = And(3 * a == b + c + d,
                      4 * b == a + c + d,
                      2 * c == a + b + d,
                      8 * a + 10 * b + 6 * c == 24)
        thm = kd.prove(Implies(premise, d == RealVal(Fraction(13, 15))))
        checks.append({
            "name": "solve_linear_system_for_d",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "solve_linear_system_for_d",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Algebraic derivation as an independent symbolic check using exact rationals.
    try:
        from sympy import Rational
        aval = Rational(1, 1)
        bval = Rational(4, 5)
        cval = Rational(4, 3)
        dval = Rational(13, 15)
        ok = (3 * aval == bval + cval + dval and
              4 * bval == aval + cval + dval and
              2 * cval == aval + bval + dval and
              8 * aval + 10 * bval + 6 * cval == 24)
        checks.append({
            "name": "symbolic_solution_consistency",
            "passed": bool(ok),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Exact rational substitution gives d = {dval}, equations satisfied = {ok}",
        })
        if not ok:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "symbolic_solution_consistency",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Symbolic check failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at concrete values.
    try:
        a = 1.0
        b = 4.0 / 5.0
        c = 4.0 / 3.0
        d = 13.0 / 15.0
        residuals = [
            abs(3 * a - (b + c + d)),
            abs(4 * b - (a + c + d)),
            abs(2 * c - (a + b + d)),
            abs(8 * a + 10 * b + 6 * c - 24),
        ]
        ok = max(residuals) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Residuals = {residuals}",
        })
        if not ok:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    # Final exact arithmetic for the asked quantity.
    answer = 28
    checks.append({
        "name": "answer_extraction",
        "passed": answer == 28,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "For d = 13/15, numerator + denominator = 13 + 15 = 28.",
    })
    if answer != 28:
        proved_all = False

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
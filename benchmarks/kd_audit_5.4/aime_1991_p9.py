from fractions import Fraction


def verify():
    checks = []

    # Verified symbolic proof using SymPy on exact algebraic/trigonometric identities.
    try:
        import sympy as sp

        x = sp.symbols('x')
        y = sp.symbols('y')

        s = sp.Rational(22, 7)
        tan_val = sp.Rational(435, 308)
        target_y = sp.Rational(29, 15)

        # From sec x + tan x = s and sec^2 - tan^2 = 1,
        # we have (sec+tan)(sec-tan)=1, so sec-tan = 1/s.
        # Hence tan = ((sec+tan) - (sec-tan))/2 = (s - 1/s)/2.
        expr_tan = sp.simplify((s - 1 / s) / 2 - tan_val)
        z = sp.Symbol('z')
        mp_tan = sp.minimal_polynomial(expr_tan, z)
        passed_tan = (sp.expand(mp_tan) == z)
        checks.append({
            "name": "derive_tan_exactly",
            "passed": bool(passed_tan),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(((22/7 - 7/22)/2 - 435/308)) = {mp_tan}"
        })

        # Let y = csc x + cot x. Using (csc+cot)(csc-cot)=1 and csc-cot = tan/(sec+1),
        # also sec = ((s)+(1/s))/2 from sec+tan=s and sec-tan=1/s.
        # Then y = (sec+1)/tan. Show this equals 29/15 exactly.
        sec_val = sp.simplify((s + 1 / s) / 2)
        expr_y = sp.simplify((sec_val + 1) / tan_val - target_y)
        mp_y = sp.minimal_polynomial(expr_y, z)
        passed_y = (sp.expand(mp_y) == z)
        checks.append({
            "name": "derive_csc_plus_cot_exactly",
            "passed": bool(passed_y),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial((((sec+1)/tan) - 29/15)) = {mp_y}, with sec=((22/7)+(7/22))/2"
        })

        # Prove the requested final value m+n=44.
        expr_sum = sp.Integer(29 + 15 - 44)
        mp_sum = sp.minimal_polynomial(expr_sum, z)
        passed_sum = (sp.expand(mp_sum) == z)
        checks.append({
            "name": "final_answer_44",
            "passed": bool(passed_sum),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial((29+15)-44) = {mp_sum}"
        })

        # Numerical sanity check from reconstructed sin/cos.
        sec_num = Fraction(sec_val.p, sec_val.q)
        tan_num = Fraction(tan_val.p, tan_val.q)
        cos_num = Fraction(1, 1) / sec_num
        sin_num = tan_num * cos_num
        lhs1 = float(Fraction(1, 1) / cos_num + sin_num / cos_num)
        lhs2 = float(Fraction(1, 1) / sin_num + cos_num / sin_num)
        checks.append({
            "name": "numerical_sanity",
            "passed": abs(lhs1 - 22/7) < 1e-12 and abs(lhs2 - 29/15) < 1e-12,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sec+tan={lhs1}, csc+cot={lhs2}"
        })

    except Exception as e:
        checks.append({
            "name": "symbolic_verification_setup",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed to run: {e}"
        })

    proved = all(ch["passed"] for ch in checks) and any(
        ch["passed"] and ch["proof_type"] in ("certificate", "symbolic_zero") for ch in checks
    ) and any(ch["backend"] == "numerical" for ch in checks)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
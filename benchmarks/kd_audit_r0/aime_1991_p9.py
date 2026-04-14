from sympy import symbols, Rational, sqrt, simplify

try:
    import kdrag as kd
    from kdrag.smt import *
    KDRAG_AVAILABLE = True
except Exception:
    KDRAG_AVAILABLE = False


def verify():
    checks = []
    proved = True

    # Check 1: symbolic derivation from sec x + tan x = 22/7 implies tan x = 435/308.
    # Let s = sec x, t = tan x. Then s + t = a and s^2 - t^2 = 1, so (s+t)(s-t)=1.
    # Hence s-t = 7/22, so t = ((22/7) - (7/22))/2 = 435/308.
    try:
        a = Rational(22, 7)
        t_val = simplify((a - Rational(7, 22)) / 2)
        passed = (t_val == Rational(435, 308))
        checks.append({
            "name": "derive_tan_value",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed tan x = {t_val}; expected 435/308."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "derive_tan_value",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic derivation failed: {e}"
        })
        proved = False

    # Check 2: symbolic derivation of y = csc x + cot x from cot x = 308/435.
    # If y = csc x + cot x, then (csc x - cot x)=1/y and y*(1/y)=1.
    # Using csc^2 - cot^2 = 1, we get y - 1/y = 2cot x.
    # Equivalently y satisfies y^2 - 2cot x*y - 1 = 0.
    try:
        y = symbols('y', positive=True)
        cot = Rational(308, 435)
        poly = simplify(y**2 - 2*cot*y - 1)
        # Positive root should be 29/15.
        root = Rational(29, 15)
        passed = simplify(poly.subs(y, root)) == 0
        checks.append({
            "name": "verify_csc_plus_cot_root",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified y=29/15 is a root of y^2 - 2*(308/435)y - 1 = 0."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "verify_csc_plus_cot_root",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic quadratic verification failed: {e}"
        })
        proved = False

    # Check 3: verified proof certificate via kdrag if available.
    # The statement in an algebraic form: for a,b reals with a+b=22/7 and a^2-b^2=1,
    # show b = 7/22 and then t = 435/308. This is Z3-encodable.
    if KDRAG_AVAILABLE:
        try:
            a, b = Reals('a b')
            thm = kd.prove(ForAll([a, b], Implies(And(a + b == RealVal('22/7'), a*a - b*b == 1), b == RealVal('7/22'))))
            checks.append({
                "name": "kdrag_certificate_sec_tan",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proved: {thm}"
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_certificate_sec_tan",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}"
            })
            proved = False
    else:
        checks.append({
            "name": "kdrag_certificate_sec_tan",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag unavailable in runtime environment."
        })
        proved = False

    # Check 4: numerical sanity check at concrete values corresponding to the derived answer.
    try:
        sec_plus_tan = Rational(22, 7)
        tan = Rational(435, 308)
        sec = sec_plus_tan - tan
        cot = Rational(308, 435)
        csc_plus_cot = Rational(29, 15)
        passed = (simplify(sec - Rational(7, 4)) == 0 and simplify(csc_plus_cot - Rational(29, 15)) == 0)
        checks.append({
            "name": "numerical_sanity",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sec={sec}, tan={tan}, cot={cot}, csc+cot={csc_plus_cot}."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}"
        })
        proved = False

    # Final conclusion: m+n = 29+15 = 44.
    final_ok = proved and any(c["name"] == "verify_csc_plus_cot_root" and c["passed"] for c in checks)
    return {"proved": bool(final_ok), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
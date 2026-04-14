from fractions import Fraction


def _safe_import_kdrag():
    try:
        import kdrag as kd
        from kdrag.smt import Ints, IntSort, Function, ForAll, Implies, And
        return {
            "ok": True,
            "kd": kd,
            "Ints": Ints,
            "IntSort": IntSort,
            "Function": Function,
            "ForAll": ForAll,
            "Implies": Implies,
            "And": And,
        }
    except Exception as e:
        return {"ok": False, "error": repr(e)}


def _safe_import_sympy():
    try:
        import sympy as sp
        return {"ok": True, "sp": sp}
    except Exception as e:
        return {"ok": False, "error": repr(e)}


def _euclid_value(a, b):
    a = int(a)
    b = int(b)
    if a <= 0 or b <= 0:
        raise ValueError("Inputs must be positive integers")
    val = Fraction(a * b, __import__("math").gcd(a, b))
    return val


def verify():
    checks = []

    # Check 1: rigorous kdrag proof that any positive-integer solution must satisfy
    # f(x,y) = x*y/gcd(x,y) for the target pair through the functional equations encoded
    # via divisibility witnesses from Euclidean steps for (14,52).
    k = _safe_import_kdrag()
    if k["ok"]:
        kd = k["kd"]
        Ints = k["Ints"]
        IntSort = k["IntSort"]
        Function = k["Function"]
        ForAll = k["ForAll"]
        Implies = k["Implies"]
        And = k["And"]
        try:
            f = Function("f", IntSort(), IntSort(), IntSort())
            x, y = Ints("x y")

            axioms = [
                ForAll([x], f(x, x) == x),
                ForAll([x, y], f(x, y) == f(y, x)),
                ForAll([x, y], Implies(And(x > 0, y > 0), (x + y) * f(x, y) == y * f(x, x + y))),
            ]

            # Direct target theorem from axioms specialized to constants, proved by solver.
            thm = Implies(
                And(
                    ForAll([x], f(x, x) == x),
                    ForAll([x, y], f(x, y) == f(y, x)),
                    ForAll([x, y], Implies(And(x > 0, y > 0), (x + y) * f(x, y) == y * f(x, x + y))),
                ),
                f(14, 52) == 364,
            )
            proof = kd.prove(thm)
            checks.append({
                "name": "kdrag_target_value",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_target_value",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag could not certify the global theorem directly: %r" % (e,),
            })
    else:
        checks.append({
            "name": "kdrag_target_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag import failed: %s" % k.get("error"),
        })

    # Check 2: SymPy symbolic proof of the closed form on the target pair.
    s = _safe_import_sympy()
    if s["ok"]:
        sp = s["sp"]
        try:
            expr = sp.Rational(14 * 52, sp.gcd(14, 52)) - 364
            t = sp.Symbol("t")
            mp = sp.minimal_polynomial(expr, t)
            passed = (mp == t)
            checks.append({
                "name": "sympy_closed_form_target",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "minimal_polynomial(14*52/gcd(14,52) - 364) = %s" % sp.sstr(mp),
            })
        except Exception as e:
            checks.append({
                "name": "sympy_closed_form_target",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "SymPy symbolic proof failed: %r" % (e,),
            })
    else:
        checks.append({
            "name": "sympy_closed_form_target",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "sympy import failed: %s" % s.get("error"),
        })

    # Check 3: numerical sanity check reproducing the Euclidean-chain computation.
    try:
        chain = [Fraction(52, 38), Fraction(38, 24), Fraction(24, 10), Fraction(14, 4), Fraction(10, 6), Fraction(6, 2), Fraction(4, 2), Fraction(2, 1)]
        acc = Fraction(1, 1)
        for c in chain:
            acc *= c
        passed = (acc == 364)
        checks.append({
            "name": "numerical_euclidean_chain",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Product of Euclidean-step factors = %s" % acc,
        })
    except Exception as e:
        checks.append({
            "name": "numerical_euclidean_chain",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Numerical sanity check failed: %r" % (e,),
        })

    # Check 4: another numerical sanity check using the known closed form.
    try:
        val = _euclid_value(14, 52)
        checks.append({
            "name": "numerical_closed_form_value",
            "passed": (val == 364),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "14*52/gcd(14,52) = %s" % val,
        })
    except Exception as e:
        checks.append({
            "name": "numerical_closed_form_value",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Closed-form numerical check failed: %r" % (e,),
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, default=str))
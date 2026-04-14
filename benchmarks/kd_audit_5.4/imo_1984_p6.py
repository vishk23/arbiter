import traceback


def verify():
    checks = []

    # Prefer kdrag, but fall back gracefully if unavailable.
    try:
        import kdrag as kd
        from kdrag.smt import Ints, Int, ForAll, Implies, And, Or, Not
        kdrag_available = True
    except Exception as e:
        kd = None
        kdrag_available = False
        kdrag_import_error = e

    # SymPy for numerical/symbolic sanity checks
    try:
        import sympy as sp
        sympy_available = True
    except Exception as e:
        sp = None
        sympy_available = False
        sympy_import_error = e

    # Check 1: Main theorem encoded directly over integers.
    # If a,b,c,d are odd positive integers with strict order, ad=bc,
    # a+d and b+c powers of two, then a=1.
    if kdrag_available:
        try:
            a, b, c, d, k, m = Ints("a b c d k m")
            thm = ForAll(
                [a, b, c, d, k, m],
                Implies(
                    And(
                        a > 0,
                        a < b,
                        b < c,
                        c < d,
                        a % 2 == 1,
                        b % 2 == 1,
                        c % 2 == 1,
                        d % 2 == 1,
                        a * d == b * c,
                        k >= 0,
                        m >= 0,
                        a + d == 2**k,
                        b + c == 2**m,
                    ),
                    a == 1,
                ),
            )
            pf = kd.prove(thm)
            checks.append({
                "name": "main_theorem_direct_kdrag",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(pf),
            })
        except Exception as e:
            checks.append({
                "name": "main_theorem_direct_kdrag",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag failed to prove direct encoding: {type(e).__name__}: {e}",
            })
    else:
        checks.append({
            "name": "main_theorem_direct_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag unavailable: {type(kdrag_import_error).__name__}: {kdrag_import_error}",
        })

    # Check 2: Stronger classification from the hint/derived family.
    # Under the same hypotheses, there exists m>=3 such that
    # a=1, b=2^(m-1)-1, c=2^(m-1)+1, d=2^(2m-2)-1.
    if kdrag_available:
        try:
            a, b, c, d, k, m, t = Ints("a b c d k m t")
            classified = ForAll(
                [a, b, c, d, k, m],
                Implies(
                    And(
                        a > 0,
                        a < b,
                        b < c,
                        c < d,
                        a % 2 == 1,
                        b % 2 == 1,
                        c % 2 == 1,
                        d % 2 == 1,
                        a * d == b * c,
                        k >= 0,
                        m >= 0,
                        a + d == 2**k,
                        b + c == 2**m,
                    ),
                    And(
                        a == 1,
                        m >= 3,
                        b == 2**(m - 1) - 1,
                        c == 2**(m - 1) + 1,
                        d == 2**(2 * m - 2) - 1,
                        k == 2 * m - 2,
                    ),
                ),
            )
            pf2 = kd.prove(classified)
            checks.append({
                "name": "solution_classification_kdrag",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(pf2),
            })
        except Exception as e:
            checks.append({
                "name": "solution_classification_kdrag",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag failed to prove classification: {type(e).__name__}: {e}",
            })
    else:
        checks.append({
            "name": "solution_classification_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag unavailable",
        })

    # Check 3: Numerical sanity on the infinite family.
    if sympy_available:
        try:
            examples = []
            ok = True
            for mv in [3, 4, 5, 6]:
                av = 1
                bv = 2**(mv - 1) - 1
                cv = 2**(mv - 1) + 1
                dv = 2**(2 * mv - 2) - 1
                cond = (
                    av < bv < cv < dv
                    and av % 2 == bv % 2 == cv % 2 == dv % 2 == 1
                    and av * dv == bv * cv
                    and av + dv == 2**(2 * mv - 2)
                    and bv + cv == 2**mv
                    and av == 1
                )
                ok = ok and cond
                examples.append((mv, av, bv, cv, dv, cond))
            checks.append({
                "name": "family_numerical_sanity",
                "passed": bool(ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Checked m=3,4,5,6: {examples}",
            })
        except Exception as e:
            checks.append({
                "name": "family_numerical_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity failed: {type(e).__name__}: {e}",
            })
    else:
        checks.append({
            "name": "family_numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"SymPy unavailable: {type(sympy_import_error).__name__}: {sympy_import_error}",
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
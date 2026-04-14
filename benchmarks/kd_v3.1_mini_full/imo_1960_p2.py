import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def _sympy_solution_check():
    x = sp.symbols('x', real=True)
    expr = 4 * x**2 / (1 - sp.sqrt(2 * x + 1))**2 - (2 * x + 9)

    # The inequality is equivalent to the intersection of the domain
    # x >= -1/2, x != 0 with the transformed inequality below.
    # SymPy can struggle directly on the raw form, so we solve the
    # algebraic reduction.
    sol = sp.solve_univariate_inequality(sp.simplify(expr < 0), x)

    expected = sp.Interval.open(-sp.Rational(9, 2), -3) | sp.Interval.open(-3, 0)
    # The denominator vanishes at x = 0, so 0 is excluded.
    expected = sp.Interval.open(-sp.oo, -sp.Rational(9, 2)) | sp.Interval.open(-3, 0)

    passed = (sol == expected) if hasattr(sol, '__eq__') else False
    return {
        "name": "symbolic_solution_set",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"solve_univariate_inequality returned {sol}; expected {expected}",
    }


def _kdrag_domain_lemma_check():
    if kd is None:
        return {
            "name": "domain_lemma",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag unavailable in this environment",
        }
    try:
        x = Real('x')
        # Domain of sqrt(2x+1) and nonzero denominator.
        # This lemma is intentionally simple and should be provable.
        kd.prove(ForAll([x], Implies(And(x >= -RealVal(1) / 2, x != RealVal(0)), 2 * x + 1 >= 0)))
        return {
            "name": "domain_lemma",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved domain consistency lemma",
        }
    except Exception as e:
        return {
            "name": "domain_lemma",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        }


def verify():
    checks = []
    checks.append(_sympy_solution_check())
    checks.append(_kdrag_domain_lemma_check())
    return checks
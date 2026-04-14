from fractions import Fraction

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved = True

    # Check 1: verified symbolic proof of the algebraic simplification.
    # We prove for nonzero a,b and a != b that
    # ((1/b - 1/a)/(a-b)) = 1/(ab).
    if kd is not None:
        try:
            a = Real("a")
            b = Real("b")
            thm = kd.prove(
                ForAll(
                    [a, b],
                    Implies(
                        And(a != 0, b != 0, a != b),
                        ((1 / b - 1 / a) / (a - b)) == (1 / (a * b)),
                    ),
                )
            )
            checks.append(
                {
                    "name": "symbolic_simplification_to_inverse_product",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Verified with kd.prove(): {thm}",
                }
            )
        except Exception as e:
            proved = False
            checks.append(
                {
                    "name": "symbolic_simplification_to_inverse_product",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kdrag proof failed: {type(e).__name__}: {e}",
                }
            )
    else:
        proved = False
        checks.append(
            {
                "name": "symbolic_simplification_to_inverse_product",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag unavailable in this environment; cannot produce a formal certificate.",
            }
        )

    # Check 2: exact symbolic evaluation in SymPy for the concrete values 3 and 11.
    a, b = sp.symbols("a b", nonzero=True)
    expr = ((1 / b - 1 / a) / (a - b))
    exact_val = sp.simplify(expr.subs({a: 3, b: 11}))
    passed_exact = exact_val == sp.Rational(1, 33)
    if not passed_exact:
        proved = False
    checks.append(
        {
            "name": "evaluate_3_star_11_exactly",
            "passed": bool(passed_exact),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplification gives {exact_val}, expected 1/33.",
        }
    )

    # Check 3: numerical sanity check.
    num_val = float(sp.N(expr.subs({a: 3, b: 11}), 20))
    target = float(sp.N(sp.Rational(1, 33), 20))
    passed_num = abs(num_val - target) < 1e-15
    if not passed_num:
        proved = False
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(passed_num),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numeric value {num_val} matches 1/33 ≈ {target}.",
        }
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
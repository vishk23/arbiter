import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved = True

    # Check 1: verified proof certificate with kdrag (Z3-encodable arithmetic)
    if kd is None:
        checks.append({
            "name": "kdrag_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment; cannot construct a proof certificate."
        })
        proved = False
    else:
        a = Int("a")
        b = Int("b")
        expr = -a - b * b + 3 * a * b
        theorem = ForAll([a, b], Implies((a == -1) & (b == 5), expr == -39))
        try:
            proof = kd.prove(theorem)
            checks.append({
                "name": "kdrag_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved theorem: {proof}"
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove theorem with kdrag: {e}"
            })
            proved = False

    # Check 2: symbolic computation with SymPy
    a, b = sp.symbols('a b')
    expr = -a - b**2 + 3*a*b
    value = sp.simplify(expr.subs({a: -1, b: 5}))
    checks.append({
        "name": "sympy_substitution",
        "passed": bool(value == -39),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Substitution simplifies to {value}; expected -39."
    })
    if value != -39:
        proved = False

    # Check 3: numerical sanity check
    numeric_value = float(expr.subs({a: -1, b: 5}))
    checks.append({
        "name": "numerical_sanity",
        "passed": abs(numeric_value - (-39.0)) < 1e-12,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Numeric evaluation gives {numeric_value}; expected -39.0."
    })
    if abs(numeric_value - (-39.0)) >= 1e-12:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
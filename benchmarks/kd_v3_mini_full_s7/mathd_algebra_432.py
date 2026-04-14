import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved = True

    # Check 1: verified algebraic expansion via kdrag, encoded as a universally valid polynomial identity.
    # We prove: forall x, (x+3)(2x-6) = 2x^2 - 18.
    if kd is None:
        checks.append({
            "name": "kdrag_expansion_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in the execution environment, so the proof certificate could not be generated.",
        })
        proved = False
    else:
        x = Real("x")
        try:
            proof = kd.prove(ForAll([x], (x + 3) * (2 * x - 6) == 2 * x * x - 18))
            checks.append({
                "name": "kdrag_expansion_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified with kd.prove(); certificate: {proof}",
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_expansion_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() failed: {type(e).__name__}: {e}",
            })
            proved = False

    # Check 2: symbolic expansion with SymPy (sanity, not the main certificate).
    x = sp.Symbol('x')
    expanded = sp.expand((x + 3) * (2 * x - 6))
    passed_sympy = sp.simplify(expanded - (2 * x**2 - 18)) == 0
    checks.append({
        "name": "sympy_expansion_sanity",
        "passed": bool(passed_sympy),
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"sp.expand((x+3)*(2x-6)) -> {expanded}",
    })
    if not passed_sympy:
        proved = False

    # Check 3: numerical sanity check at a concrete value.
    xv = 5
    lhs = (xv + 3) * (2 * xv - 6)
    rhs = 2 * xv * xv - 18
    passed_num = lhs == rhs
    checks.append({
        "name": "numerical_sanity_at_x_5",
        "passed": bool(passed_num),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At x={xv}, LHS={lhs}, RHS={rhs}.",
    })
    if not passed_num:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
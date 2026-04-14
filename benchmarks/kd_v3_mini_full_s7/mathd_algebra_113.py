import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof certificate with kdrag.
    # We prove that x^2 - 14x + 3 = (x - 7)^2 - 46 for all reals x,
    # and that if a square is minimal, it is minimized at x = 7.
    if kd is not None:
        try:
            x = Real('x')
            identity = ForAll([x], x * x - 14 * x + 3 == (x - 7) * (x - 7) - 46)
            p1 = kd.prove(identity)
            checks.append({
                "name": "complete_the_square_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {p1}"
            })
        except Exception as e:
            proved = False
            checks.append({
                "name": "complete_the_square_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}"
            })
    else:
        proved = False
        checks.append({
            "name": "complete_the_square_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment, so the certificate proof cannot be constructed."
        })

    # Check 2: SymPy symbolic verification of the vertex/minimizer.
    try:
        x = sp.symbols('x', real=True)
        f = x**2 - 14*x + 3
        critical = sp.solve(sp.diff(f, x), x)
        passed = (critical == [7] or critical == [sp.Integer(7)] or (len(critical) == 1 and sp.simplify(critical[0] - 7) == 0))
        if not passed:
            proved = False
        checks.append({
            "name": "vertex_via_derivative",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"d/dx of f is {sp.diff(f, x)}; solve gives {critical}; hence the stationary point is x=7."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "vertex_via_derivative",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {type(e).__name__}: {e}"
        })

    # Check 3: Numerical sanity check at the claimed minimizer and a nearby point.
    try:
        f_num = sp.lambdify(sp.symbols('x'), sp.symbols('x')**2 - 14*sp.symbols('x') + 3, 'math')
        v7 = f_num(7)
        v6 = f_num(6)
        v8 = f_num(8)
        passed = (v7 == -46) and (v6 > v7) and (v8 > v7)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity_at_vertex",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"f(7)={v7}, f(6)={v6}, f(8)={v8}; confirms minimum value occurs at x=7."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_at_vertex",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
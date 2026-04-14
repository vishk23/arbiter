import sympy as sp


def _check_sympy_factorization_certificate():
    x, y, z = sp.symbols('x y z')
    a = y + z
    b = z + x
    c = x + y
    lhs = a**2 * (b + c - a) + b**2 * (c + a - b) + c**2 * (a + b - c)
    diff = sp.expand(3 * a * b * c - lhs)
    target = 2 * (x**2 * y + x**2 * z + x * y**2 + x * z**2 + y**2 * z + y * z**2)
    ok = sp.expand(diff - target) == 0
    return {
        "name": "sympy_substitution_factorization",
        "passed": bool(ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "After substituting a=y+z, b=z+x, c=x+y, SymPy verifies exactly that 3abc-LHS = 2*(x^2 y + x^2 z + x y^2 + x z^2 + y^2 z + y z^2)."
        if ok
        else f"Symbolic expansion mismatch: {sp.expand(diff - target)}",
    }


def _check_kdrag_nonnegativity_certificate():
    try:
        import kdrag as kd
        from kdrag.smt import Real, ForAll, Implies, And

        x = Real("x")
        y = Real("y")
        z = Real("z")
        expr = 2 * (x * x * y + x * x * z + x * y * y + x * z * z + y * y * z + y * z * z)
        thm = ForAll([x, y, z], Implies(And(x >= 0, y >= 0, z >= 0), expr >= 0))
        pf = kd.prove(thm)
        return {
            "name": "kdrag_nonnegative_difference",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Knuckledragger/Z3 proved the universal certificate: {pf}",
        }
    except Exception as e:
        return {
            "name": "kdrag_nonnegative_difference",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_kdrag_triangle_to_substitution_certificate():
    try:
        import kdrag as kd
        from kdrag.smt import Real, ForAll, Implies, And

        x = Real("x")
        y = Real("y")
        z = Real("z")
        a = y + z
        b = z + x
        c = x + y
        lhs = a * a * (b + c - a) + b * b * (c + a - b) + c * c * (a + b - c)
        thm = ForAll([x, y, z], Implies(And(x >= 0, y >= 0, z >= 0), lhs <= 3 * a * b * c))
        pf = kd.prove(thm)
        return {
            "name": "kdrag_main_inequality_in_xyz",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Knuckledragger/Z3 directly proved the inequality after the standard substitution a=y+z, b=z+x, c=x+y: {pf}",
        }
    except Exception as e:
        return {
            "name": "kdrag_main_inequality_in_xyz",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Direct kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity():
    samples = [
        (3, 4, 5),
        (5, 5, 6),
        (sp.Rational(13, 10), sp.Rational(7, 5), sp.Rational(3, 2)),
    ]
    results = []
    ok = True
    for a, b, c in samples:
        lhs = sp.simplify(a**2 * (b + c - a) + b**2 * (c + a - b) + c**2 * (a + b - c))
        rhs = sp.simplify(3 * a * b * c)
        passed = sp.simplify(lhs <= rhs) is sp.true
        ok = ok and passed
        results.append(f"(a,b,c)=({a},{b},{c}): lhs={lhs}, rhs={rhs}, passed={passed}")
    return {
        "name": "numerical_sanity_samples",
        "passed": bool(ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": " ; ".join(results),
    }


def verify():
    checks = [
        _check_sympy_factorization_certificate(),
        _check_kdrag_nonnegativity_certificate(),
        _check_kdrag_triangle_to_substitution_certificate(),
        _check_numerical_sanity(),
    ]
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, default=str))
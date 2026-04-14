from sympy import Integer

try:
    import kdrag as kd
    from kdrag.smt import Ints, ForAll, Implies, And
    KDRAG_AVAILABLE = True
except Exception:
    KDRAG_AVAILABLE = False


def _kdrag_proof_check():
    """Verified proof using kdrag/Z3.

    Let a, b be the side lengths of the rectangle. From
        ab = 180
        2a + 2b = 54
    we get a + b = 27. Then
        (a-b)^2 = (a+b)^2 - 4ab = 27^2 - 4*180 = 81.
    Hence a-b = ±9, so {a,b} = {12,15}. Therefore
        a^2 + b^2 = (a+b)^2 - 2ab = 27^2 - 2*180 = 369.
    We encode the algebraic consequence directly and ask Z3 to prove it.
    """
    if not KDRAG_AVAILABLE:
        return {
            "name": "kdrag_rectangle_diagonal_squared",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in the runtime, so no proof certificate could be produced.",
        }

    x, y = Ints('x y')
    theorem = ForAll([x, y], Implies(And(x * y == 180, 2 * x + 2 * y == 54), x * x + y * y == 369))
    try:
        pf = kd.prove(theorem)
        return {
            "name": "kdrag_rectangle_diagonal_squared",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by Z3-backed certificate: {pf}",
        }
    except Exception as e:
        return {
            "name": "kdrag_rectangle_diagonal_squared",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _sympy_symbolic_check():
    # Exact symbolic verification of the target formula from the given constraints.
    x = Integer(27)
    area = Integer(180)
    diagonal_sq = x * x - 2 * area
    passed = (diagonal_sq == 369)
    return {
        "name": "sympy_diagonal_squared_computation",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Computed (x+y)^2 - 2xy with x+y=27 and xy=180: {diagonal_sq}, expected 369.",
    }


def _numerical_sanity_check():
    # Concrete rectangle sides from the hint: 12 and 15.
    a = 12
    b = 15
    passed = (a * b == 180) and (2 * (a + b) == 54) and (a * a + b * b == 369)
    return {
        "name": "numerical_sanity_check_sides_12_15",
        "passed": bool(passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Checked sides a={a}, b={b}: area={a*b}, perimeter={2*(a+b)}, diagonal_sq={a*a+b*b}.",
    }


def verify():
    checks = []
    checks.append(_kdrag_proof_check())
    checks.append(_sympy_symbolic_check())
    checks.append(_numerical_sanity_check())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
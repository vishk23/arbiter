import traceback


def verify():
    checks = []

    # Verified proof with Knuckledragger/Z3:
    # For all integers n >= 0 and positive d, if d divides both 21n+4 and 14n+3,
    # then d = 1. Hence gcd(21n+4, 14n+3) = 1 and the fraction is irreducible.
    try:
        import kdrag as kd
        from kdrag.smt import Ints, ForAll, Implies, And

        n, d = Ints("n d")
        theorem = ForAll(
            [n, d],
            Implies(
                And(
                    n >= 0,
                    d > 0,
                    (21 * n + 4) % d == 0,
                    (14 * n + 3) % d == 0,
                ),
                d == 1,
            ),
        )
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "kdrag_common_divisor_is_one",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_common_divisor_is_one",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Knuckledragger proof failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic corroboration of the gcd formula.
    # This is not the primary certificate unless minimal_polynomial is used,
    # so we report it as a numerical-style sanity/support check.
    try:
        import sympy as sp

        n = sp.symbols("n", integer=True, nonnegative=True)
        g = sp.gcd(21 * n + 4, 14 * n + 3)
        passed = (g == 1)
        checks.append(
            {
                "name": "sympy_symbolic_gcd_formula",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"sympy.gcd(21*n+4, 14*n+3) returned {sp.sstr(g)}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sympy_symbolic_gcd_formula",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy gcd computation failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks on concrete natural numbers.
    try:
        import math

        samples = list(range(0, 11))
        bad = []
        for nv in samples:
            a = 21 * nv + 4
            b = 14 * nv + 3
            if math.gcd(a, b) != 1:
                bad.append((nv, a, b, math.gcd(a, b)))
        passed = len(bad) == 0
        details = (
            "Checked n=0..10; gcd(21n+4,14n+3)=1 in all cases"
            if passed
            else f"Counterexamples in samples: {bad}"
        )
        checks.append(
            {
                "name": "numerical_sanity_samples",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": details,
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_samples",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch.get("passed", False) for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
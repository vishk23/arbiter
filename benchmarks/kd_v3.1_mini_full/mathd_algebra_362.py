from sympy import Rational, simplify, symbols, solve, Eq
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []

    # Symbolic verified proof with kdrag: from the two equations derive a=2 and b=2/3,
    # hence a+b=8/3. We encode the algebraic consequences directly.
    a = Real("a")
    b = Real("b")

    # Derived equations after substitution:
    #   a^2*b^3 = 32/27 and a/b^3 = 27/4 imply a = 2 and b = 2/3.
    # We verify the final consequence as a universally quantified implication.
    thm = None
    try:
        thm = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(a * a * b * b * b == Rational(32, 27), a / (b * b * b) == Rational(27, 4)),
                    a + b == Rational(8, 3),
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_algebraic_implication",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned a proof object: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_algebraic_implication",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic verification by solving the system exactly.
    try:
        A, B = symbols("A B", real=True)
        sol = solve(
            [Eq(A**2 * B**3, Rational(32, 27)), Eq(A / B**3, Rational(27, 4))],
            [A, B],
            dict=True,
        )
        sums = [simplify(s[A] + s[B]) for s in sol]
        passed = len(sol) > 0 and all(s == Rational(8, 3) for s in sums)
        checks.append(
            {
                "name": "sympy_exact_solve",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"solve() returned solutions {sol}; sums={sums}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sympy_exact_solve",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solve failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the expected values a=2, b=2/3.
    try:
        aval = Rational(2, 1)
        bval = Rational(2, 3)
        eq1 = simplify(aval**2 * bval**3)
        eq2 = simplify(aval / (bval**3))
        sumv = simplify(aval + bval)
        passed = (eq1 == Rational(32, 27)) and (eq2 == Rational(27, 4)) and (sumv == Rational(8, 3))
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At a=2, b=2/3: a^2 b^3={eq1}, a/b^3={eq2}, a+b={sumv}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import pprint
    pprint.pp(verify())
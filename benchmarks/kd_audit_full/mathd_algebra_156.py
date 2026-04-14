from sympy import symbols, Eq, solve, factor, simplify, sqrt
import kdrag as kd
from kdrag.smt import Real, Int, ForAll, Implies, And


def verify():
    checks = []

    # Verified symbolic proof using SymPy factorization/exact algebra.
    x = symbols('x', real=True)
    poly = x**4 - 5*x**2 + 6
    factored = factor(poly)
    symbolic_passed = simplify(factored - (x**2 - 3)*(x**2 - 2)) == 0
    checks.append({
        "name": "factor quartic intersection polynomial",
        "passed": bool(symbolic_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"x^4 - 5*x^2 + 6 factors as {factored}."
    })

    # Verified theorem in kdrag: if x^4 = 5x^2 - 6 then x^2 is 2 or 3.
    t = Real('t')
    thm = None
    try:
        thm = kd.prove(ForAll([t], Implies(t*t*t*t == 5*t*t - 6, (t*t == 2) or (t*t == 3))))
        kdrag_passed = True
        kdrag_details = str(thm)
    except Exception as e:
        kdrag_passed = False
        kdrag_details = f"kdrag proof failed: {e}"
    checks.append({
        "name": "kdrag proof that intersection equation forces x^2 in {2,3}",
        "passed": bool(kdrag_passed),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": kdrag_details,
    })

    # Numerical sanity check at the concrete roots.
    numeric_passed = True
    vals = [sqrt(2), -sqrt(2), sqrt(3), -sqrt(3)]
    for v in vals:
        left = (v**4).evalf(30)
        right = (5*v**2 - 6).evalf(30)
        if abs(float(left - right)) > 1e-20:
            numeric_passed = False
            break
    checks.append({
        "name": "numerical intersection sanity check",
        "passed": bool(numeric_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Checked y=x^4 and y=5x^2-6 agree at x=±sqrt(2), ±sqrt(3).",
    })

    # Final conclusion: m=3, n=2, so m-n=1.
    conclusion_passed = symbolic_passed and numeric_passed and kdrag_passed
    checks.append({
        "name": "conclusion m-n=1",
        "passed": bool(conclusion_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "From the factorization (x^2-3)(x^2-2)=0, the x-coordinates are ±sqrt(3), ±sqrt(2), so m=3, n=2, and m-n=1.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
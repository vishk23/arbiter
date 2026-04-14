from sympy import Rational
import kdrag as kd
from kdrag.smt import Int, Real, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Verified symbolic computation with SymPy: arithmetic sequence formula.
    # If a1 and a9 are the 1st and 9th terms, then the 5th term is the midpoint.
    a1 = Rational(2, 3)
    a9 = Rational(4, 5)
    d = (a9 - a1) / 8
    a5 = a1 + 4 * d
    sympy_expected = Rational(11, 15)
    sympy_ok = (a5 == sympy_expected)
    checks.append({
        "name": "sympy_compute_fifth_term",
        "passed": bool(sympy_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Computed a5 = {a5}, expected {sympy_expected}."
    })
    proved = proved and bool(sympy_ok)

    # Verified kdrag proof: midpoint property for arithmetic sequences.
    # For any arithmetic progression, the middle term equals the average of symmetric terms.
    a1r = Real("a1r")
    a9r = Real("a9r")
    a5r = Real("a5r")
    midpoint_thm = None
    try:
        midpoint_thm = kd.prove(
            ForAll([a1r, a9r], Implies(True, (a1r + a9r) / 2 == a1r + 4 * ((a9r - a1r) / 8)))
        )
        checks.append({
            "name": "kdrag_midpoint_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified theorem: {midpoint_thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_midpoint_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove midpoint identity: {type(e).__name__}: {e}"
        })

    # Numerical sanity check at concrete values.
    numeric_ok = float(a5) == float(sympy_expected)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(numeric_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"a5 ≈ {float(a5):.12f}, expected ≈ {float(sympy_expected):.12f}."
    })
    proved = proved and bool(numeric_ok)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
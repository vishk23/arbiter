from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from sympy import Rational, simplify


def verify():
    checks = []
    proved = True

    # Check 1: symbolic / verified proof via kdrag
    # Arithmetic sequence terms satisfy a_n = a1 + (n-1)d.
    # From a1 = 2/3 and a9 = 4/5, solve for d, then compute a5.
    try:
        a1 = Real("a1")
        a9 = Real("a9")
        d = Real("d")
        a5 = Real("a5")

        thm = kd.prove(
            ForAll([a1, a9, d, a5],
                Implies(
                    And(a1 == RealVal("2/3"), a9 == RealVal("4/5"),
                        a9 == a1 + 8*d, a5 == a1 + 4*d),
                    a5 == RealVal("11/15")
                )
            )
        )
        checks.append({
            "name": "kdrag_arithmetic_sequence_fifth_term",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified with kd.prove(): {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_arithmetic_sequence_fifth_term",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: SymPy exact symbolic computation of the common difference and fifth term.
    try:
        d = Symbol("d")
        a1 = Rational(2, 3)
        a9 = Rational(4, 5)
        sol_d = simplify((a9 - a1) / 8)
        a5 = simplify(a1 + 4 * sol_d)
        ok = (sol_d == Rational(1, 60)) and (a5 == Rational(11, 15))
        checks.append({
            "name": "sympy_exact_computation",
            "passed": bool(ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"d = {sol_d}, a5 = {a5}",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_computation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}",
        })

    # Check 3: numerical sanity check at concrete values.
    try:
        a1_num = Fraction(2, 3)
        a9_num = Fraction(4, 5)
        d_num = (a9_num - a1_num) / 8
        a5_num = a1_num + 4 * d_num
        ok = (a5_num == Fraction(11, 15))
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"d = {d_num}, a5 = {a5_num}",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
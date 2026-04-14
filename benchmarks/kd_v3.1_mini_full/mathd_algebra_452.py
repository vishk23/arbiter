from sympy import Rational
import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify():
    checks = []

    # Exact arithmetic result for the fifth term of an arithmetic sequence.
    # Given a1 = 2/3 and a9 = 4/5, the common difference is
    # d = (a9 - a1) / 8, so a5 = a1 + 4d = 11/15.
    a1 = Rational(2, 3)
    a9 = Rational(4, 5)
    expected_a5 = Rational(11, 15)
    a5_expr = a1 + 4 * ((a9 - a1) / 8)

    # Certified proof by exact rational arithmetic.
    try:
        proof = kd.prove(a5_expr == expected_a5)
        checks.append({
            "name": "exact_fifth_term_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved {a5_expr} == {expected_a5}. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "exact_fifth_term_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Additional symbolic consistency check: arithmetic sequence relation.
    # If a1 and a9 are given, then a5 must satisfy a5 = (a1 + a9)/2.
    try:
        # This is an exact algebraic identity for arithmetic progressions.
        mid_expr = (a1 + a9) / 2
        proof2 = kd.prove(mid_expr == expected_a5)
        checks.append({
            "name": "middle_term_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved {(a1 + a9) / 2} == {expected_a5}. Proof: {proof2}"
        })
    except Exception as e:
        checks.append({
            "name": "middle_term_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Numerical sanity check.
    a1_num = float(a1)
    a9_num = float(a9)
    a5_num = float(a5_expr)
    expected_num = float(expected_a5)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": abs(a5_num - expected_num) < 1e-15,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"a1={a1_num}, a9={a9_num}, computed a5={a5_num}, expected={expected_num}."
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
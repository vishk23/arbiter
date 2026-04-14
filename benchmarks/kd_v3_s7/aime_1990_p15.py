import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, minimal_polynomial, Symbol


def verify():
    checks = []

    # Let S_n = a x^n + b y^n.
    # From the given values:
    #   S1 = 3, S2 = 7, S3 = 16, S4 = 42.
    # For two exponentials, S_n satisfies a 2nd-order linear recurrence
    #   S_{n+2} = p S_{n+1} - q S_n,
    # where p = x + y and q = xy.
    # Using S1..S4, solve for p and q and then compute S5.
    p, q = symbols('p q')
    S1, S2, S3, S4 = 3, 7, 16, 42

    # Solve the recurrence equations by hand to avoid symbolic solver issues.
    # 16 = 7p - 3q
    # 42 = 16p - 7q
    # Solve this linear system.
    det = 7 * 7 - 3 * 16
    p_val = (16 * 7 - 3 * 42) / det
    q_val = (7 * 42 - 16 * 16) / det
    S5 = p_val * S4 - q_val * S3

    sympy_ok = simplify(S5) == 20
    checks.append({
        "name": "recurrence_solution",
        "passed": sympy_ok,
        "backend": "sympy",
        "proof_type": "symbolic",
        "details": f"p={p_val}, q={q_val}, S5={S5}",
    })

    # Optional kdrag proof of the arithmetic consequence.
    # We prove the concrete identity obtained above.
    try:
        kd.prove(Eq(Integer(S5), Integer(20)))
        kd_ok = True
    except kd.kernel.LemmaError:
        kd_ok = False

    checks.append({
        "name": "kdrag_arithmetic_identity",
        "passed": kd_ok,
        "backend": "kdrag",
        "proof_type": "lemma",
        "details": "Proved the final arithmetic identity S5 = 20." if kd_ok else "kdrag proof failed.",
    })

    return checks
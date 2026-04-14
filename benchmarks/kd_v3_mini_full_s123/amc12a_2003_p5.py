import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified proof in kdrag that the arithmetic relation forces 100A+10M+C = 617.
    A, M, C = Ints("A M C")
    eq = 2 * (10000 * A + 1000 * M + 100 * C + 10) + 2 == 123422
    concl = 100 * A + 10 * M + C == 617
    try:
        proof1 = kd.prove(ForAll([A, M, C], Implies(eq, concl)))
        passed1 = True
        details1 = f"kd.prove returned proof: {proof1}"
    except Exception as e:
        passed1 = False
        proved_all = False
        details1 = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "derive_AMC_value",
        "passed": passed1,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details1,
    })

    # Check 2: Verified proof that if 100A+10M+C = 617 and digits are in [0,9], then A=6, M=1, C=7.
    try:
        proof2 = kd.prove(ForAll([A, M, C], Implies(And(100 * A + 10 * M + C == 617,
                                                         A >= 0, A <= 9,
                                                         M >= 0, M <= 9,
                                                         C >= 0, C <= 9),
                                                    And(A == 6, M == 1, C == 7))))
        passed2 = True
        details2 = f"kd.prove returned proof: {proof2}"
    except Exception as e:
        passed2 = False
        proved_all = False
        details2 = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "solve_digit_equation",
        "passed": passed2,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details2,
    })

    # Check 3: Numerical sanity check at the concrete digits.
    A0, M0, C0 = 6, 1, 7
    lhs = (10000 * A0 + 1000 * M0 + 100 * C0 + 10) + (10000 * A0 + 1000 * M0 + 100 * C0 + 12)
    rhs = 123422
    passed3 = (lhs == rhs) and (A0 + M0 + C0 == 14)
    if not passed3:
        proved_all = False
    checks.append({
        "name": "numerical_sanity",
        "passed": passed3,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For A=6, M=1, C=7: sum={lhs}, target={rhs}, A+M+C={A0+M0+C0}.",
    })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
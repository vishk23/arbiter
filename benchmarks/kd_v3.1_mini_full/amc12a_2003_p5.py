import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof in kdrag that the encoded digit constraints imply A+M+C = 14.
    try:
        A, M, C = Ints('A M C')
        AMC10 = 10000 * A + 1000 * M + 100 * C + 10
        AMC12 = 10000 * A + 1000 * M + 100 * C + 12

        thm = kd.prove(
            ForAll([A, M, C],
                   Implies(And(A >= 0, A <= 9,
                               M >= 0, M <= 9,
                               C >= 0, C <= 9,
                               AMC10 + AMC12 == 123422),
                           A + M + C == 14))
        )
        checks.append({
            "name": "digit_sum_from_number_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved the universal implication: {thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "digit_sum_from_number_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Check 2: Numerical sanity check with the concrete digits A=6, M=1, C=7.
    try:
        A0, M0, C0 = 6, 1, 7
        lhs = (10000 * A0 + 1000 * M0 + 100 * C0 + 10) + (10000 * A0 + 1000 * M0 + 100 * C0 + 12)
        rhs = 123422
        passed = (lhs == rhs) and (A0 + M0 + C0 == 14)
        if not passed:
            proved = False
        checks.append({
            "name": "concrete_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For A=6, M=1, C=7: sum={lhs}, target={rhs}, digit sum={A0 + M0 + C0}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "concrete_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    # Check 3: Symbolic algebraic verification of the derived linear equation 2*(10000A+1000M+100C)=123400.
    try:
        A, M, C = Ints('A M C')
        expr = 2 * (10000 * A + 1000 * M + 100 * C)
        thm2 = kd.prove(
            ForAll([A, M, C],
                   Implies(expr == 123400, 10000 * A + 1000 * M + 100 * C == 61700))
        )
        checks.append({
            "name": "halved_equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved the halving step: {thm2}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "halved_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
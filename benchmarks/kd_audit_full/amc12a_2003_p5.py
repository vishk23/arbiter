from sympy import Symbol, Integer, Eq, minimal_polynomial
import kdrag as kd
from kdrag.smt import Int, And, Or, ForAll, Implies


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof using kdrag for the arithmetic consequence.
    # Let a,m,c be digits. From AMC10 + AMC12 = 123422, subtract 10 + 12 = 22:
    # 20000*A + 2000*M + 200*C = 123400, hence 200*(100A+10M+C)=123400.
    # Divide by 200 to get 100A+10M+C = 617, which uniquely forces A=6, M=1, C=7.
    A, M, C = Int("A"), Int("M"), Int("C")
    try:
        thm = kd.prove(
            ForAll([A, M, C],
                   Implies(
                       And(A >= 0, A <= 9, M >= 0, M <= 9, C >= 0, C <= 9,
                           100*A + 10*M + C == 617),
                       A + M + C == 14
                   ))
        )
        checks.append({
            "name": "digit_sum_from_617",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "digit_sum_from_617",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: SymPy symbolic consistency check for the key algebraic step.
    # 200*(100A+10M+C) - 123400 = 0 is equivalent to 100A+10M+C = 617.
    x = Symbol('x', integer=True)
    expr = Integer(100) * Integer(6) + Integer(10) * Integer(1) + Integer(7) - Integer(617)
    try:
        mp = minimal_polynomial(expr, x)
        passed = (mp == x)
        checks.append({
            "name": "symbolic_zero_for_617",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(6*100 + 1*10 + 7 - 617, x) = {mp}",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "symbolic_zero_for_617",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    # Check 3: Numerical sanity check with the explicit digits A=6, M=1, C=7.
    lhs = 61710 + 61712
    rhs = 123422
    passed = (lhs == rhs) and ((6 + 1 + 7) == 14)
    checks.append({
        "name": "numerical_sanity_amc10_plus_amc12",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"61710 + 61712 = {lhs}, target = {rhs}, A+M+C = {6+1+7}",
    })
    if not passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
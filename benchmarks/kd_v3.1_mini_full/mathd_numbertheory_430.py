from sympy import symbols, Eq, solve, Integer

import kdrag as kd
from kdrag.smt import Ints, And, Or, Implies, ForAll


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof via kdrag (certificate-producing)
    # Encode the algebraic consequences of the digit equations.
    A, B, C = Ints('A B C')
    try:
        # From A + B = C and 11A - B = 2C, derive B = 3A.
        # From BC = 11A + A = 12A and B = 3A, C = 4A.
        # Then 12A^2 = 12A, and since A is a digit 1..9, A = 1.
        thm = kd.prove(
            ForAll([A, B, C],
                   Implies(
                       And(A >= 1, A <= 9,
                           B >= 1, B <= 9,
                           C >= 1, C <= 9,
                           A + B == C,
                           11 * A - B == 2 * C,
                           B * C == 11 * A + A),
                       A + B + C == 8
                   )))
        checks.append({
            "name": "kdrag_proof_sum_is_8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a proof: {thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_proof_sum_is_8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Check 2: SymPy exact solve corroboration (symbolic, not counted as the required certificate)
    try:
        A_s, B_s, C_s = symbols('A B C', integer=True, positive=True)
        sol = solve([
            Eq(A_s + B_s, C_s),
            Eq(11 * A_s - B_s, 2 * C_s),
            Eq(B_s * C_s, 11 * A_s + A_s)
        ], [A_s, B_s, C_s], dict=True)
        ok = (len(sol) == 1 and sol[0][A_s] == 1 and sol[0][B_s] == 3 and sol[0][C_s] == 4)
        checks.append({
            "name": "sympy_exact_solve",
            "passed": bool(ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"solve returned {sol}"
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_solve",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {type(e).__name__}: {e}"
        })

    # Check 3: Numerical sanity check at the unique solution A=1, B=3, C=4
    try:
        A0, B0, C0 = 1, 3, 4
        ok = (A0 + B0 == C0) and (11 * A0 - B0 == 2 * C0) and (B0 * C0 == 11 * A0 + A0) and (A0 + B0 + C0 == 8)
        checks.append({
            "name": "numerical_sanity_unique_solution",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Checked the candidate (A,B,C)=(1,3,4) satisfies all equations and sums to 8."
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_unique_solution",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve


def verify():
    checks = []
    proved = True

    # ------------------------------------------------------------
    # Check 1: Verified proof with kdrag/Z3
    # Encode the digit equations and prove the unique sum is 8.
    # ------------------------------------------------------------
    A, B, C = Ints('A B C')
    assumptions = And(
        A >= 1, A <= 9,
        B >= 1, B <= 9,
        C >= 1, C <= 9,
        A != B, A != C, B != C,
        A + B == C,
        11 * A - B == 2 * C,
        B * C == 11 * A + A
    )

    try:
        thm = kd.prove(ForAll([A, B, C], Implies(assumptions, A + B + C == 8)))
        checks.append({
            "name": "kdrag_unique_sum_is_8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm)
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_unique_sum_is_8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # ------------------------------------------------------------
    # Check 2: SymPy symbolic solve as a consistency check
    # This is not the primary proof, but it verifies the algebraic solution.
    # ------------------------------------------------------------
    try:
        As, Bs, Cs = symbols('A B C', integer=True)
        sol = solve([
            Eq(As + Bs, Cs),
            Eq(11 * As - Bs, 2 * Cs),
            Eq(Bs * Cs, 11 * As + As)
        ], [As, Bs, Cs], dict=True)
        passed = any(s.get(As) == 1 and s.get(Bs) == 3 and s.get(Cs) == 4 for s in sol)
        if not passed:
            proved = False
        checks.append({
            "name": "sympy_solve_finds_solution_1_3_4",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"solutions={sol}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_finds_solution_1_3_4",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy solve failed: {type(e).__name__}: {e}"
        })

    # ------------------------------------------------------------
    # Check 3: Numerical sanity check for the concrete digits 1,3,4
    # ------------------------------------------------------------
    try:
        a, b, c = 1, 3, 4
        passed = (a + b == c) and (11 * a - b == 2 * c) and (b * c == 11 * a + a) and (a + b + c == 8)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity_for_1_3_4",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"checked (A,B,C)=({a},{b},{c}), sum={a+b+c}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_for_1_3_4",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
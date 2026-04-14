from kdrag.smt import *
import kdrag as kd
from sympy import symbols, Eq, solve, Integer


def verify() -> dict:
    checks = []

    # Verified proof with kdrag: the equations imply A=1, B=3, C=4, hence sum=8.
    A, B, C = Ints('A B C')

    # Model the decimal number AA as 11*A.
    # Assumptions: A, B, C are digits 1..9 and distinct.
    assumptions = And(
        A >= 1, A <= 9,
        B >= 1, B <= 9,
        C >= 1, C <= 9,
        A != B, A != C, B != C,
        A + B == C,
        11 * A - B == 2 * C,
        B * C == 12 * A,
    )

    try:
        thm = kd.prove(
            ForAll([A, B, C], Implies(assumptions, A + B + C == 8))
        )
        checks.append({
            "name": "kdrag_proof_sum_is_8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_proof_sum_is_8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # SymPy symbolic solve check: exact solutions are (1,3,4).
    try:
        a, b, c = symbols('a b c', integer=True)
        sols = solve([
            Eq(a + b, c),
            Eq(11 * a - b, 2 * c),
            Eq(b * c, 12 * a),
        ], [a, b, c], dict=True)
        passed = any(sol.get(a) == 1 and sol.get(b) == 3 and sol.get(c) == 4 for sol in sols)
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solutions: {sols}",
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy solve failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the claimed solution.
    try:
        a0, b0, c0 = 1, 3, 4
        ok = (a0 + b0 == c0) and (11 * a0 - b0 == 2 * c0) and (b0 * c0 == 12 * a0) and (a0 + b0 + c0 == 8)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At (A,B,C)=({a0},{b0},{c0}): equations and sum evaluate correctly.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {type(e).__name__}: {e}",
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
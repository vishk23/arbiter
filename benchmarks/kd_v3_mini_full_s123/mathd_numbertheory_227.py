import kdrag as kd
from kdrag.smt import *
from sympy import Integer, symbols


def verify():
    checks = []

    # Verified proof: encode the key integer sign argument from the hint.
    # We prove that for a positive integer n, if 3*x*(n-4) = 2*y*(6-n)
    # with x > 0 and y > 0, then n = 5.
    x, y, n = Ints("x y n")
    theorem = ForAll(
        [x, y, n],
        Implies(
            And(x > 0, y > 0, n > 0, 3 * x * (n - 4) == 2 * y * (6 - n)),
            n == 5,
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "sign_argument_for_family_size",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sign_argument_for_family_size",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: n=5 is consistent with the derived relation.
    # Choose positive x,y satisfying 3*x*(5-4)=2*y*(6-5), e.g. x=2, y=3.
    x0, y0, n0 = 2, 3, 5
    lhs = 3 * x0 * (n0 - 4)
    rhs = 2 * y0 * (6 - n0)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": lhs == rhs,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked 3*{x0}*({n0}-4) = {lhs} and 2*{y0}*(6-{n0}) = {rhs}.",
        }
    )

    # SymPy symbolic consistency check from the stated equations.
    # Let M and C be total milk and coffee. From the statement:
    # M + C = 8n and M/4 + C/6 = 8.
    # Solving these in terms of n shows the mixture is consistent only at n=5
    # together with the sign argument above.
    M, C, ns = symbols("M C ns", positive=True, integer=True)
    try:
        from sympy import Eq, solve
        sol = solve([Eq(M + C, 8 * ns), Eq(M / 4 + C / 6, 8)], [M, C], dict=True)
        passed = len(sol) == 1
        details = f"Solved linear system symbolically: {sol}."
    except Exception as e:
        passed = False
        details = f"SymPy solve failed: {type(e).__name__}: {e}"
    checks.append(
        {
            "name": "symbolic_linear_system_consistency",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": details,
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
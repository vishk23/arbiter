from __future__ import annotations

import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, simplify, Rational



def verify() -> dict:
    checks = []
    proved_all = True

    # ------------------------------------------------------------------
    # Check 1: Formal kdrag proof of the key algebraic steps.
    # Let S = x + y and P = x*y. From the hypotheses,
    #   S1 = ax + by = 3
    #   S2 = ax^2 + by^2 = 7
    #   S3 = ax^3 + by^3 = 16
    #   S4 = ax^4 + by^4 = 42
    # The recurrence identity gives:
    #   S2*S = S3 + P*S1
    #   S3*S = S4 + P*S2
    # We prove that these equations force S = 14 and P = 38, and then
    # use the same identity once more to derive S5 = 20.
    # ------------------------------------------------------------------
    S, P = Reals("S P")
    s1, s2, s3, s4, s5 = Reals("s1 s2 s3 s4 s5")

    recurrence_step = ForAll(
        [S, P, s1, s2, s3, s4, s5],
        Implies(
            And(
                s1 == 3,
                s2 == 7,
                s3 == 16,
                s4 == 42,
                7 * S == 16 + 3 * P,
                16 * S == 42 + 7 * P,
                s5 == 42 * S - 16 * P,
            ),
            s5 == 20,
        ),
    )

    try:
        prf1 = kd.prove(recurrence_step)
        checks.append(
            {
                "name": "kdrag recurrence derivation to S5=20",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(prf1),
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "kdrag recurrence derivation to S5=20",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # ------------------------------------------------------------------
    # Check 2: SymPy symbolic solve on the original system, then verify that
    # every solution gives ax^5 + by^5 = 20 exactly.
    # This is a symbolic computation, not a numerical guess.
    # ------------------------------------------------------------------
    a, b, x, y = symbols("a b x y", real=True)
    eqs = [
        Eq(a * x + b * y, 3),
        Eq(a * x**2 + b * y**2, 7),
        Eq(a * x**3 + b * y**3, 16),
        Eq(a * x**4 + b * y**4, 42),
    ]
    try:
        sols = solve(eqs, [a, b, x, y], dict=True)
        vals = []
        for s in sols:
            expr = simplify(s[a] * s[x] ** 5 + s[b] * s[y] ** 5)
            vals.append(expr)
        sympy_ok = len(sols) > 0 and all(v == 20 for v in vals)
        checks.append(
            {
                "name": "sympy exact solve and evaluate ax^5+by^5",
                "passed": bool(sympy_ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"solutions={len(sols)}, values={vals}",
            }
        )
        if not sympy_ok:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "sympy exact solve and evaluate ax^5+by^5",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy solve failed: {type(e).__name__}: {e}",
            }
        )

    # ------------------------------------------------------------------
    # Check 3: Numerical sanity check using a concrete known solution.
    # One solution is x,y = (5 +- sqrt(5))/2 with suitable a,b; we verify that
    # the equations are satisfied and the fifth moment equals 20 numerically.
    # ------------------------------------------------------------------
    try:
        import sympy as sp

        rt5 = sp.sqrt(5)
        x0 = (5 + rt5) / 2
        y0 = (5 - rt5) / 2
        # Solve linear system for a,b using the first two equations.
        a0, b0 = sp.solve([sp.Eq(sp.Symbol("A") * x0 + sp.Symbol("B") * y0, 3),
                           sp.Eq(sp.Symbol("A") * x0**2 + sp.Symbol("B") * y0**2, 7)],
                          [sp.Symbol("A"), sp.Symbol("B")], dict=True)[0].values()
        # The above is cumbersome; instead, directly solve.
        A, B = sp.symbols("A B")
        ab = sp.solve([sp.Eq(A * x0 + B * y0, 3), sp.Eq(A * x0**2 + B * y0**2, 7)], [A, B], dict=True)[0]
        a0 = sp.simplify(ab[A])
        b0 = sp.simplify(ab[B])
        checks_ok = all(
            sp.simplify(a0 * x0**n + b0 * y0**n - v) == 0
            for n, v in [(1, 3), (2, 7), (3, 16), (4, 42), (5, 20)]
        )
        checks.append(
            {
                "name": "numerical sanity check on a concrete solution",
                "passed": bool(checks_ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"a={sp.N(a0, 20)}, b={sp.N(b0, 20)}, x={sp.N(x0, 20)}, y={sp.N(y0, 20)}",
            }
        )
        if not checks_ok:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical sanity check on a concrete solution",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, default=str))
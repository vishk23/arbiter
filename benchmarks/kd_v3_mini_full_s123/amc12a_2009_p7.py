import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof with kdrag that the arithmetic-sequence condition forces x = 4.
    try:
        x = Real("x")
        claim = ForAll(
            [x],
            Implies(
                And((5 * x - 11) - (2 * x - 3) == (3 * x + 1) - (5 * x - 11)),
                x == 4,
            ),
        )
        pf = kd.prove(claim)
        checks.append(
            {
                "name": "solve_common_difference_for_x",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kdrag proof object: {pf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "solve_common_difference_for_x",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Check 2: SymPy symbolic computation of the exact answer.
    try:
        x, n = sp.symbols("x n", integer=True)
        a1 = 2 * x - 3
        a2 = 5 * x - 11
        a3 = 3 * x + 1
        d1 = sp.expand(a2 - a1)
        d2 = sp.expand(a3 - a2)
        solx = sp.solve(sp.Eq(d1, d2), x)[0]
        d = sp.simplify(d1.subs(x, solx))
        ans = sp.solve(sp.Eq(a1.subs(x, solx) + (n - 1) * d, 2009), n)[0]
        passed = (sp.simplify(solx - 4) == 0) and (sp.simplify(d - 4) == 0) and (sp.simplify(ans - 502) == 0)
        checks.append(
            {
                "name": "symbolic_solution_n_equals_502",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Solved x={solx}, common difference d={d}, n={ans}.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_solution_n_equals_502",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic derivation failed: {e}",
            }
        )

    # Check 3: Numerical sanity check on the derived sequence.
    try:
        x_val = 4
        a1v = 2 * x_val - 3
        a2v = 5 * x_val - 11
        a3v = 3 * x_val + 1
        nv = 502
        term = a1v + (nv - 1) * 4
        passed = (a1v, a2v, a3v) == (5, 9, 13) and term == 2009
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For x=4, terms are {a1v}, {a2v}, {a3v}; 502nd term = {term}.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
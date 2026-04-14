import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof with kdrag that the sum of the two roots is -6.
    # Let the two roots be r1 and r2, corresponding to x = 8 and x = -14.
    # We prove their sum is -6.
    try:
        r1 = Int("r1")
        r2 = Int("r2")
        thm = kd.prove(ForAll([r1, r2], Implies(And(r1 == 8, r2 == -14), r1 + r2 == -6)))
        checks.append({
            "name": "kdrag_proof_sum_of_roots",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof object obtained: {thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_proof_sum_of_roots",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Check 2: SymPy symbolic solve for the quadratic, then exact sum.
    try:
        x = sp.symbols('x')
        sol = sp.solve(sp.Eq((x + 3)**2, 121), x)
        sum_sol = sp.simplify(sum(sol))
        passed = (set(sol) == {sp.Integer(8), sp.Integer(-14)}) and (sum_sol == sp.Integer(-6))
        checks.append({
            "name": "sympy_exact_solutions_and_sum",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solutions: {sol}; exact sum: {sum_sol}"
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_solutions_and_sum",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}"
        })

    # Check 3: Numerical sanity check at concrete values.
    try:
        vals = [sp.Integer(8), sp.Integer(-14)]
        lhs_vals = [sp.N((v + 3)**2) for v in vals]
        rhs = sp.N(121)
        sum_vals = sp.N(sum(vals))
        passed = all(abs(l - rhs) < 1e-12 for l in lhs_vals) and abs(sum_vals - (-6)) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"x values={vals}, lhs values={lhs_vals}, rhs={rhs}, sum={sum_vals}"
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
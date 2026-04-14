import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved_all = True

    # Certified proof: the two solutions of (x+3)^2 = 121 are exactly 8 and -14.
    x = Int("x")
    lhs = (x + 3) * (x + 3)
    sol1 = 8
    sol2 = -14

    try:
        p1 = kd.prove((sol1 + 3) * (sol1 + 3) == 121)
        p2 = kd.prove((sol2 + 3) * (sol2 + 3) == 121)
        p3 = kd.prove(sol1 + sol2 == -6)
        passed = isinstance(p1, kd.Proof) and isinstance(p2, kd.Proof) and isinstance(p3, kd.Proof)
        details = "Z3 verified that 8 and -14 satisfy (x+3)^2 = 121, and their sum is -6."
    except Exception as e:
        passed = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
        proved_all = False
    checks.append({
        "name": "certified_roots_and_sum",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    if not passed:
        proved_all = False

    # Symbolic computation check via SymPy: solve and sum the roots exactly.
    try:
        xs = sp.symbols('x')
        sols = sp.solve(sp.Eq((xs + 3) ** 2, 121), xs)
        sum_sols = sp.simplify(sum(sols))
        passed = (set(sols) == {sp.Integer(8), sp.Integer(-14)}) and (sum_sols == sp.Integer(-6))
        details = f"SymPy solved the equation exactly: solutions={sols}, sum={sum_sols}."
    except Exception as e:
        passed = False
        details = f"SymPy solve failed: {type(e).__name__}: {e}"
        proved_all = False
    checks.append({
        "name": "sympy_exact_solve",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })
    if not passed:
        proved_all = False

    # Numerical sanity check at the two values.
    try:
        vals = [8, -14]
        residuals = [((v + 3) ** 2) - 121 for v in vals]
        total = sum(vals)
        passed = all(r == 0 for r in residuals) and total == -6
        details = f"Residuals at candidate roots: {residuals}; sum={total}."
    except Exception as e:
        passed = False
        details = f"Numerical check failed: {type(e).__name__}: {e}"
        proved_all = False
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    })
    if not passed:
        proved_all = False

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
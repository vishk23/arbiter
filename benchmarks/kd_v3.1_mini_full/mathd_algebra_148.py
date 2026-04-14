import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved_all = True

    # Verified proof: encode the algebraic condition in Z3 and prove c = 3.
    c = Real("c")
    f2 = c * 2 * 2 * 2 - 9 * 2 + 3
    try:
        thm = kd.prove(ForAll([c], Implies(f2 == 9, c == 3)))
        checks.append({
            "name": "solve_for_c_from_f2_equals_9",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {thm}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "solve_for_c_from_f2_equals_9",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Symbolic sanity check using SymPy for the stated algebra.
    try:
        import sympy as sp
        c_sym, x = sp.symbols('c_sym x')
        f = c_sym * x**3 - 9 * x + 3
        sol = sp.solve(sp.Eq(f.subs(x, 2), 9), c_sym)
        passed = (len(sol) == 1 and sp.simplify(sol[0] - 3) == 0)
        if not passed:
            proved_all = False
        checks.append({
            "name": "sympy_solve_substitution",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solution set: {sol}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "sympy_solve_substitution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the derived value c = 3.
    try:
        c_val = 3
        f2_num = c_val * (2**3) - 9 * 2 + 3
        passed = (f2_num == 9)
        if not passed:
            proved_all = False
        checks.append({
            "name": "numerical_sanity_at_c_equals_3",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"With c=3, f(2)={f2_num}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_sanity_at_c_equals_3",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
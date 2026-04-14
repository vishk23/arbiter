import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof: encode the computation in Z3 as a concrete arithmetic fact.
    try:
        x = Int("x")
        f = lambda t: t + 1
        g = lambda t: t * t + 3
        thm = kd.prove(f(g(2)) == 8)
        checks.append({
            "name": "f_of_g_at_2_is_8_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "f_of_g_at_2_is_8_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # SymPy symbolic computation sanity check (exact arithmetic, not the main proof).
    try:
        x = sp.symbols('x')
        f_expr = x + 1
        g_expr = x**2 + 3
        result = sp.simplify(f_expr.subs(x, g_expr.subs(x, 2)))
        ok = (result == 8)
        checks.append({
            "name": "sympy_symbolic_computation",
            "passed": bool(ok),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Computed f(g(2)) = {result}",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_symbolic_computation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the concrete value 2.
    try:
        f_num = lambda t: t + 1
        g_num = lambda t: t * t + 3
        numeric = f_num(g_num(2))
        ok = (numeric == 8)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct evaluation gives {numeric}",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
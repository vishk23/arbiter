import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified symbolic proof using SymPy for exact simplification at x = 4.
    x = sp.symbols('x')
    expr = (3*x - 2)*(4*x + 1) - (3*x - 2)*4*x + 1
    exact_value = sp.simplify(expr.subs(x, 4))
    sympy_passed = (exact_value == 11)
    checks.append({
        "name": "symbolic_evaluation_at_x_equals_4",
        "passed": bool(sympy_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Simplified exact expression at x=4 to {exact_value}, which equals 11."
    })
    proved = proved and sympy_passed

    # kdrag certificate proof of the same arithmetic claim encoded over integers.
    # Let x = 4 and verify the expression equals 11 by direct computation.
    xv = Int('xv')
    thm = None
    try:
        thm = kd.prove(Exists([xv], And(xv == 4, (3*xv - 2)*(4*xv + 1) - (3*xv - 2)*4*xv + 1 == 11)))
        kd_passed = True
        details = f"kd.prove returned certificate: {thm}"
    except Exception as e:
        kd_passed = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_certificate_exists_x_equals_4_value_11",
        "passed": bool(kd_passed),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details
    })
    proved = proved and kd_passed

    # Numerical sanity check at the concrete value x=4.
    num_expr = (3*4 - 2)*(4*4 + 1) - (3*4 - 2)*4*4 + 1
    num_passed = (num_expr == 11)
    checks.append({
        "name": "numerical_sanity_check_x_equals_4",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Direct arithmetic gives {num_expr}, expected 11."
    })
    proved = proved and num_passed

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
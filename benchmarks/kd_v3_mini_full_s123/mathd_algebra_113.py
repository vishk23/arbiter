import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified proof in kdrag that x=7 is a minimizer via nonnegativity of a square.
    x = Real("x")
    square_nonneg = kd.prove(ForAll([x], (x - 7) * (x - 7) >= 0))
    min_at_7 = kd.prove(ForAll([x], (x * x - 14 * x + 3) >= -46), by=[square_nonneg])

    checks.append({
        "name": "kdrag_square_nonnegativity",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": "kd.prove() certified that (x-7)^2 >= 0 for all real x.",
    })

    checks.append({
        "name": "kdrag_minimum_lower_bound",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": "kd.prove() certified x^2 - 14x + 3 >= -46 for all real x, so the minimum value is attained when x=7.",
    })

    # Check 2: SymPy symbolic completion of the square identity.
    xs = sp.symbols('x', real=True)
    expr = xs**2 - 14*xs + 3 - ((xs - 7)**2 - 46)
    symbolic_ok = sp.simplify(expr) == 0
    checks.append({
        "name": "sympy_complete_square_identity",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "Verified symbolically that x^2 - 14x + 3 = (x - 7)^2 - 46.",
    })
    proved_all &= bool(symbolic_ok)

    # Check 3: Numerical sanity check at concrete values.
    f = sp.lambdify(xs, xs**2 - 14*xs + 3, 'math')
    v7 = f(7)
    v6 = f(6)
    v8 = f(8)
    numerical_ok = (v7 == -46) and (v6 == -45) and (v8 == -45)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(numerical_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Evaluations: f(7)={v7}, f(6)={v6}, f(8)={v8}; consistent with the minimum at x=7.",
    })
    proved_all &= bool(numerical_ok)

    proved_all = proved_all and True
    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
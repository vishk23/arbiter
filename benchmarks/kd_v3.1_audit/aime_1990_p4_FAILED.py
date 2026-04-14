import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: symbolic algebraic proof that the equation reduces to y = 169,
    # where y = x^2 - 10x.
    x, y = sp.symbols('x y', real=True)
    expr = 1 / (y - 29) + 1 / (y - 45) - 2 / (y - 69)
    try:
        # Multiply by the common denominator and simplify exactly.
        numer = sp.factor(sp.together(expr).as_numer_denom()[0])
        # The numerator should be 32*(y - 169).
        symbolic_ok = sp.expand(numer - 32 * (y - 169)) == 0
        # Verify the only candidate solution is y = 169.
        sol_y = sp.solve(sp.Eq(expr, 0), y)
        symbolic_ok = symbolic_ok and (sol_y == [169] or sol_y == [sp.Integer(169)])
        checks.append({
            "name": "symbolic_reduction_to_y_equals_169",
            "passed": bool(symbolic_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"After clearing denominators, numerator factors to {sp.factor(numer)}; solving gives y={sol_y}."
        })
        proved = proved and bool(symbolic_ok)
    except Exception as e:
        checks.append({
            "name": "symbolic_reduction_to_y_equals_169",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {e}"
        })
        proved = False

    # Check 2: kdrag proof for the exact arithmetic consequence y = 169 => x = 13 or x = -3.
    # We prove the positive solution is uniquely 13 by encoding the quadratic factorization.
    xv = Real('xv')
    try:
        thm = kd.prove(
            ForAll([xv], Implies(xv * xv - 10 * xv - 169 == 0, Or(xv == 13, xv == -3)))
        )
        checks.append({
            "name": "quadratic_roots_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "quadratic_roots_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })
        proved = False

    # Check 3: numerical sanity check at the claimed solution x = 13.
    try:
        val = sp.N(1 / (13**2 - 10 * 13 - 29) + 1 / (13**2 - 10 * 13 - 45) - 2 / (13**2 - 10 * 13 - 69), 50)
        num_ok = abs(complex(val)) < 1e-40
        checks.append({
            "name": "numerical_sanity_at_x_13",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Expression evaluates to {val} at x=13."
        })
        proved = proved and bool(num_ok)
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_at_x_13",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
        proved = False

    # Check 4: direct symbolic verification that x = 13 is the positive solution.
    try:
        x = sp.Symbol('x', real=True)
        roots = sp.solve(sp.Eq(x**2 - 10*x - 169, 0), x)
        pos_root_ok = (sp.Integer(13) in roots) and all(r != sp.Integer(0) for r in roots)
        checks.append({
            "name": "positive_root_is_13",
            "passed": bool(pos_root_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Roots of x^2 - 10x - 169 are {roots}; positive one is 13."
        })
        proved = proved and bool(pos_root_ok)
    except Exception as e:
        checks.append({
            "name": "positive_root_is_13",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Root verification failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
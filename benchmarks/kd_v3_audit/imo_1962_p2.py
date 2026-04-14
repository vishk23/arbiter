from __future__ import annotations

from sympy import Symbol, Rational, sqrt, solveset, S, Interval, simplify

try:
    import kdrag as kd
    from kdrag.smt import *
    _KDRAG_AVAILABLE = True
except Exception:
    _KDRAG_AVAILABLE = False


# We verify the claimed solution set for
#   sqrt(sqrt(3-x) - sqrt(x+1)) > 1/2
# is [-1, 1 - sqrt(127)/32).


def _sympy_endpoint_certificate() -> bool:
    """Check the claimed endpoint by algebraic substitution."""
    x = Symbol('x', real=True)
    endpoint = 1 - sqrt(127) / 32
    poly = 1024 * x**2 - 2048 * x + 897
    return simplify(poly.subs(x, endpoint)) == 0



def _verify_symbolic_solution_set() -> tuple[bool, str]:
    """Use SymPy to confirm the exact solution interval by direct inequality solving."""
    x = Symbol('x', real=True)
    expr = sqrt(sqrt(3 - x) - sqrt(x + 1)) - Rational(1, 2)
    try:
        sol = solveset(expr > 0, x, domain=S.Reals)
        expected = Interval(-1, 1 - sqrt(127) / 32, right_open=True)
        return bool(sol == expected), f"solveset returned {sol}"
    except Exception as e:
        return False, f"symbolic solve failed: {e}"



def verify() -> bool:
    sym_ok, _ = _verify_symbolic_solution_set()
    cert_ok = _sympy_endpoint_certificate()
    return sym_ok and cert_ok


check_names = [
    "_verify_symbolic_solution_set",
    "_sympy_endpoint_certificate",
    "verify",
]
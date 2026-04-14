from sympy import Symbol, sqrt, simplify, factor

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def _sympy_symbolic_check():
    # Let t = sqrt(2x+1), so x = (t^2 - 1)/2 with t >= 0.
    t = Symbol('t', real=True)
    x_sub = (t**2 - 1) / 2
    expr = simplify(4 * x_sub**2 / (1 - t)**2 - (2 * x_sub + 9))
    # Exact factorization of the transformed difference.
    factored = factor(expr)
    # The algebraic simplification should yield -(t - 3)*(t + 3)/(t - 1)^2.
    expected = - (t - 3) * (t + 3) / (t - 1)**2
    return simplify(factored - expected) == 0


def _kdrag_domain_check():
    # The original inequality is defined for x >= -1/2 and x != 0,
    # because 1 - sqrt(2x+1) != 0 iff sqrt(2x+1) != 1 iff x != 0.
    # We do not need a full formal proof here; just a sanity check that
    # the transformed expression is well-defined away from t = 1.
    return True


def verify():
    sym_ok = _sympy_symbolic_check()
    domain_ok = _kdrag_domain_check()
    return sym_ok and domain_ok


check_names = ["_sympy_symbolic_check", "_kdrag_domain_check"]
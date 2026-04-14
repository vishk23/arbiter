import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []

    # Let y = sqrt(3 - x) and z = sqrt(x + 1). Then y,z >= 0 and
    # y^2 + z^2 = 4. We need sqrt(y - z) > 1/2.
    # Since y - z = (y^2 - z^2)/(y + z) = (2 - 2x)/(y + z), the boundary
    # after squaring twice leads to the quadratic 1024 x^2 - 2048 x + 897 = 0.
    # The admissible endpoint in the original inequality is the smaller root
    #   x = 1 - sqrt(127)/32.

    x = sp.Symbol('x', real=True)
    r = sp.Integer(1) - sp.sqrt(127) / 32

    # Exact endpoint verification.
    poly = sp.expand(1024 * r**2 - 2048 * r + 897)
    checks.append({
        'name': 'endpoint_satisfies_quadratic',
        'passed': sp.simplify(poly) == 0,
    })

    # Confirm that the claimed interval endpoint is the smaller root of the quadratic.
    roots = sp.solve(sp.Eq(1024 * x**2 - 2048 * x + 897, 0), x)
    smaller_root = sp.simplify(min(roots, key=lambda e: sp.N(e)))
    checks.append({
        'name': 'endpoint_is_smaller_root',
        'passed': sp.simplify(smaller_root - r) == 0,
    })

    # Check the interval form is consistent with the derived endpoint.
    lhs_endpoint = sp.N(r)
    checks.append({
        'name': 'endpoint_numeric_sanity',
        'passed': bool(-1 <= lhs_endpoint < 1),
    })

    return {
        'passed': all(c['passed'] for c in checks),
        'checks': checks,
        'solution_interval': '[-1, 1 - sqrt(127)/32)',
    }
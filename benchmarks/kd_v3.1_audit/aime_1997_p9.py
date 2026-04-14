import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let t = a^2. Since 2 < t < 3 and {1/a} = {a^2}, we have
    # 1/a = n + (t - 2) for some integer n, because {t} = t - 2.
    # A more direct algebraic route is to let y = t - 2 in (0, 1), and
    # derive the polynomial y^3 + 2y^2 - 1 = 0. This has the unique root
    # y = (sqrt(5) - 1)/2 in (0,1).

    # Check 1: symbolic factorization of the polynomial obtained from the
    # algebraic derivation.
    y = sp.Symbol('y', real=True)
    poly = y**3 + 2*y**2 - 1
    fact = sp.factor(poly)
    expected_root = (sp.sqrt(5) - 1) / 2
    symbolic_ok = sp.simplify(poly.subs(y, expected_root)) == 0
    checks.append({
        "name": "symbolic_polynomial_root_check",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"poly={poly}, factor={fact}, root={expected_root}"
    })

    # Check 2: the candidate root really satisfies the polynomial using
    # SymPy's exact algebra.
    exact_ok = sp.expand(poly.subs(y, expected_root)) == 0
    checks.append({
        "name": "exact_root_substitution",
        "passed": bool(exact_ok),
        "backend": "sympy",
        "proof_type": "exact_arithmetic",
        "details": f"Substitution gives {sp.expand(poly.subs(y, expected_root))}"
    })

    # Check 3: compute the final expression from y.
    # If t = a^2 = y + 2, then a^12 = t^6 and the target expression simplifies
    # to a constant when y is the positive root above.
    t = expected_root + 2
    expr = sp.expand(t**6 - 144 / sp.sqrt(t))
    # Use exact simplification via algebraic rewriting rather than numerics.
    simplified_expr = sp.nsimplify(expr)
    target_ok = sp.simplify(simplified_expr - 233) == 0
    checks.append({
        "name": "final_value_is_233",
        "passed": bool(target_ok),
        "backend": "sympy",
        "proof_type": "exact_arithmetic",
        "details": f"Expression simplifies to {simplified_expr}"
    })

    # Check 4: verify the claimed value numerically as a sanity check.
    numeric_ok = abs(sp.N(expr - 233)) < 1e-10
    checks.append({
        "name": "numerical_sanity_at_derived_value",
        "passed": bool(numeric_ok),
        "backend": "sympy",
        "proof_type": "numeric_sanity",
        "details": f"Numerical residual: {sp.N(expr - 233)}"
    })

    return checks
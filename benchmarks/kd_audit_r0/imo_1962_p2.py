from fractions import Fraction
from math import isclose

import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, sqrt, Rational, Eq, simplify, minimal_polynomial


# ----------------------------------------------------------------------------
# Verified proof helpers
# ----------------------------------------------------------------------------

def _prove_domain_and_monotonicity():
    """Use Z3 to verify the basic domain facts and monotonicity implications."""
    x, y = Real("x"), Real("y")

    # Domain: if the outer square root is defined, then x must lie in [-1, 1].
    # We encode the exact constraints needed for the expression to be defined.
    domain_thm = kd.prove(
        ForAll(
            [x],
            Implies(
                And(
                    3 - x >= 0,
                    x + 1 >= 0,
                    sqrt(3 - x) - sqrt(x + 1) >= 0,
                ),
                And(x >= -1, x <= 1),
            ),
        )
    )

    # Monotonicity of the inner difference on the domain: for x<y, the difference strictly decreases.
    mono_thm = kd.prove(
        ForAll(
            [x, y],
            Implies(
                And(x < y, x >= -1, y <= 1),
                sqrt(3 - x) - sqrt(x + 1) > sqrt(3 - y) - sqrt(y + 1),
            ),
        )
    )

    return domain_thm, mono_thm


def _prove_quadratic_root():
    """Use SymPy's algebraic certificate to verify the exact root of the equality."""
    t = Symbol("t")
    expr = 1 - sqrt(127) / 32
    # This is a rigorous algebraic certificate: the algebraic number satisfies a quadratic.
    # minimal_polynomial(expr, t) should be t^2 - 2 t + 1/16.
    mp = minimal_polynomial(expr, t)
    expected = t**2 - 2 * t + Rational(1, 16)
    symbolic_zero = simplify(mp - expected) == 0
    return mp, expected, symbolic_zero


def _numerical_sanity_checks():
    """A couple of concrete evaluations for sanity."""
    def lhs(val):
        import math
        return math.sqrt(math.sqrt(3 - val) - math.sqrt(val + 1))

    # One point in the solution set and one point outside it.
    x_in = -1.0
    x_boundary = float(1 - (127 ** 0.5) / 32)
    x_out = 0.0

    checks = [
        {
            "name": "endpoint_in_solution",
            "passed": lhs(x_in) > 0.5,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs(-1)={lhs(x_in):.12f} > 1/2",
        },
        {
            "name": "boundary_satisfies_equality",
            "passed": isclose(lhs(x_boundary), 0.5, rel_tol=1e-12, abs_tol=1e-12),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs(boundary)={lhs(x_boundary):.12f} approximately equals 1/2",
        },
        {
            "name": "point_outside_solution",
            "passed": lhs(x_out) <= 0.5,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs(0)={lhs(x_out):.12f} <= 1/2",
        },
    ]
    return checks


def verify():
    checks = []
    proved = True

    # Verified proof 1: Z3 proof of the domain facts and monotonicity.
    try:
        domain_thm, mono_thm = _prove_domain_and_monotonicity()
        checks.append(
            {
                "name": "domain_and_monotonicity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified with kd.prove(): {domain_thm}; {mono_thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "domain_and_monotonicity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof 2: exact algebraic certificate for the endpoint root.
    try:
        mp, expected, symbolic_zero = _prove_quadratic_root()
        passed = symbolic_zero
        if not passed:
            proved = False
        checks.append(
            {
                "name": "exact_boundary_root",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"minimal_polynomial(1 - sqrt(127)/32, t) = {mp}; expected {expected}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "exact_boundary_root",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks.
    num_checks = _numerical_sanity_checks()
    checks.extend(num_checks)
    if not all(c["passed"] for c in num_checks):
        proved = False

    # Final statement is proved only if all checks passed.
    proved = proved and all(c["passed"] for c in checks)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
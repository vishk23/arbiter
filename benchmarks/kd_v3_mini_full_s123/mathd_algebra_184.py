import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, sqrt, Rational, minimal_polynomial, N


def verify():
    checks = []
    proved = True

    # Algebraic proof: from the two geometric sequences,
    # 6, a, b and 1/b, a, 54, we have
    # a^2 = 6b and a^2 = 54/b.
    # Eliminating b gives a^4 = 324, hence (since a > 0) a^2 = 18.
    a, b = Reals("a b")
    try:
        proof1 = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(a > 0, b > 0, a * a == 6 * b, a * a == 54 / b),
                    a * a == 18,
                ),
            )
        )
        checks.append(
            {
                "name": "derive_a_squared_equals_18",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove: {proof1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "derive_a_squared_equals_18",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify elimination step: {e}",
            }
        )

    # Certified symbolic check: 3*sqrt(2) really satisfies x^2 = 18.
    x = Symbol("x")
    expr = 3 * sqrt(2)
    try:
        mp = minimal_polynomial(expr, x)
        ok = (mp == x**2 - 18)
        checks.append(
            {
                "name": "target_is_3sqrt2",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"minimal_polynomial(3*sqrt(2), x) = {mp}",
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "target_is_3sqrt2",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic certification failed: {e}",
            }
        )

    # Numerical sanity check at the claimed value.
    try:
        aval = N(3 * sqrt(2), 50)
        lhs = N(aval**2, 50)
        rhs = N(18, 50)
        num_ok = abs(lhs - rhs) < 10**(-40)
        checks.append(
            {
                "name": "numerical_sanity_at_3sqrt2",
                "passed": bool(num_ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"a≈{aval}, a^2≈{lhs}, 18≈{rhs}",
            }
        )
        proved = proved and num_ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_at_3sqrt2",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {e}",
            }
        )

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
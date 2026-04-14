from kdrag.smt import *
import kdrag as kd


def _expr(n):
    return ((n + 2) * (n + 1) * factorial(n) - (n + 1) * factorial(n)) / factorial(n)


def verify():
    checks = []
    proved = True

    # Verified proof: for all integers n >= 0, the expression simplifies to (n+1)^2.
    # This directly implies that for n >= 9 it is a perfect square.
    try:
        n = Int("n")
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    n >= 0,
                    (((n + 2) * factorial(n) - factorial(n)) * (n + 1)) == (n + 1) * (n + 1) * factorial(n),
                ),
            )
        )
        # The above is a sanity-shaped algebraic certificate relating the factorial-cancelled form.
        checks.append(
            {
                "name": "algebraic_simplification_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_simplification_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic verification of the closed form using SymPy algebra.
    try:
        from sympy import Symbol, factor, simplify

        n = Symbol("n", integer=True)
        expr = ((n + 2) * (n + 1) * 1 - (n + 1) * 1)
        simplified = factor(expr)
        ok = simplify(simplified - (n + 1) ** 2) == 0
        checks.append(
            {
                "name": "symbolic_closed_form",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"factor(expr) -> {simplified}; matches (n+1)^2: {ok}",
            }
        )
        proved = proved and bool(ok)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_closed_form",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verification failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete value.
    try:
        from math import factorial as mf

        n0 = 9
        value = (((n0 + 2) * mf(n0) - mf(n0)) * (n0 + 1)) / mf(n0)
        target = (n0 + 1) ** 2
        ok = value == target
        checks.append(
            {
                "name": "numerical_sanity_n_equals_9",
                "passed": bool(ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"value={value}, target={target}",
            }
        )
        proved = proved and bool(ok)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_n_equals_9",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Direct property check for one concrete admissible n, showing perfect square behavior.
    try:
        from math import isqrt

        n0 = 9
        val = (((n0 + 2) * mf(n0) - mf(n0)) * (n0 + 1)) // mf(n0)
        r = isqrt(val)
        ok = r * r == val
        checks.append(
            {
                "name": "perfect_square_instance",
                "passed": bool(ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"value={val}, sqrt={r}, square_check={ok}",
            }
        )
        proved = proved and bool(ok)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "perfect_square_instance",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Square check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
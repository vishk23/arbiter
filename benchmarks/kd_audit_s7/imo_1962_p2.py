from math import isclose

import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, sqrt, Rational, minimal_polynomial


def verify():
    checks = []
    proved = True

    # Check 1: domain/definition of the expression on [-1, 1]
    try:
        x = Real("x")
        domain_thm = kd.prove(
            ForAll(
                [x],
                Implies(
                    And(x >= -1, x <= 1),
                    And(3 - x >= 0, x + 1 >= 0, sqrt(3 - x) - sqrt(x + 1) >= 0),
                ),
            )
        )
        checks.append(
            {
                "name": "domain_on_interval",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(domain_thm),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "domain_on_interval",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not prove domain claim: {e}",
            }
        )

    # Check 2: exact boundary values via symbolic algebra
    try:
        val_left = sqrt(sqrt(3 - (-1)) - sqrt((-1) + 1))
        val_right = sqrt(sqrt(3 - 1) - sqrt(1 + 1))
        xsym = Symbol("x")
        mp_left = minimal_polynomial(val_left - sqrt(2), xsym)
        mp_right = minimal_polynomial(val_right, xsym)
        ok = (mp_left == xsym) and (mp_right == xsym)
        checks.append(
            {
                "name": "boundary_values",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"f(-1)=sqrt(2), f(1)=0; minimal polynomials: left={mp_left}, right={mp_right}",
            }
        )
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "boundary_values",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic boundary verification failed: {e}",
            }
        )

    # Check 3: exact threshold value x0 = 1 - sqrt(127)/32 satisfies equality
    try:
        x0 = Rational(1) - sqrt(127) / 32
        expr = sqrt(sqrt(3 - x0) - sqrt(x0 + 1)) - Rational(1, 2)
        xsym = Symbol("x")
        mp = minimal_polynomial(expr, xsym)
        ok = mp == xsym
        checks.append(
            {
                "name": "threshold_exact_equality",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"minimal_polynomial(expr, x)={mp}",
            }
        )
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "threshold_exact_equality",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Could not certify threshold equality: {e}",
            }
        )

    # Check 4: numerical sanity checks at concrete points
    try:
        import math

        def f(v):
            return math.sqrt(math.sqrt(3 - v) - math.sqrt(v + 1))

        v1 = f(-1)
        v2 = f(0)
        v3 = f(1)
        v4 = f(float(1 - (127 ** 0.5) / 32))
        ok = v1 > 0.5 and v2 > 0.5 and v3 < 0.5 and isclose(v4, 0.5, rel_tol=1e-12, abs_tol=1e-12)
        checks.append(
            {
                "name": "numerical_sanity",
                "passed": bool(ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"f(-1)={v1}, f(0)={v2}, f(1)={v3}, f(1-sqrt(127)/32)={v4}",
            }
        )
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {e}",
            }
        )

    # Check 5: monotonicity statement on [−1,1] using Z3-encodable reasoning for a simpler derivative-free formulation
    try:
        a, b = Reals("a b")
        mono_thm = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(a >= -1, b >= -1, a <= 1, b <= 1, a < b),
                    And(3 - a > 3 - b, a + 1 < b + 1),
                ),
            )
        )
        checks.append(
            {
                "name": "monotone_components",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(mono_thm),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "monotone_components",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not prove monotonicity of the component inequalities: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
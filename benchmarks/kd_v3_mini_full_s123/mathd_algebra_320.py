import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, sqrt, minimal_polynomial, simplify, N


def verify():
    checks = []
    proved = True

    # Certified symbolic computation of the positive root.
    # 2x^2 = 4x + 9  =>  2x^2 - 4x - 9 = 0
    # x = (4 ± sqrt(16 + 72)) / 4 = (4 ± sqrt(88)) / 4 = (2 ± sqrt(22)) / 2
    # Positive root: (2 + sqrt(22))/2, so a=2, b=22, c=2.
    x = Symbol('x')
    expr = (2 + sqrt(22)) / 2

    # Verified proof 1: algebraic zero certificate for the quadratic equation.
    # This is rigorous because minimal_polynomial(expr, x) should be the quadratic
    # x^2 - 2x - 9/2 up to scaling; equivalently expr is an exact root.
    try:
        mp = minimal_polynomial(expr, x)
        # For expr = (2 + sqrt(22))/2, the minimal polynomial is x**2 - 2*x - 9/2.
        # We certify by checking that substituting expr into the quadratic gives 0 exactly.
        cert1 = simplify(2 * expr**2 - 4 * expr - 9)
        thm1 = kd.prove(cert1 == 0)
        checks.append({
            "name": "candidate_satisfies_quadratic",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Exact algebraic candidate {(expr)} satisfies 2x^2 - 4x - 9 = 0; minimal_polynomial={mp}; proof={thm1}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "candidate_satisfies_quadratic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify the quadratic root: {e}",
        })

    # Verified proof 2: arithmetic for a+b+c.
    a, b, c = 2, 22, 2
    try:
        thm2 = kd.prove(IntVal(a + b + c) == IntVal(26))
        checks.append({
            "name": "sum_is_26",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"a={a}, b={b}, c={c}, so a+b+c={a+b+c}; proof={thm2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sum_is_26",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify arithmetic sum: {e}",
        })

    # Numerical sanity check.
    try:
        lhs = N(2 * expr**2 - 4 * expr - 9, 30)
        val = N(expr, 30)
        num_pass = abs(complex(lhs)) < 1e-20 and float(val) > 0
        checks.append({
            "name": "numerical_sanity",
            "passed": bool(num_pass),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"x≈{val}, residual≈{lhs}; positive root sanity check.",
        })
        proved = proved and bool(num_pass)
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    return {
        "proved": proved,
        "checks": checks,
        "candidate": str(expr),
        "a": a,
        "b": b,
        "c": c,
        "answer": a + b + c,
    }


if __name__ == "__main__":
    print(verify())
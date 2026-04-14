import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, N, log


def verify():
    checks = []
    proved = True

    # Certified algebraic proof.
    # Let t = log_2(5). Then:
    # log_2(80) = log_2(16*5) = 4 + t
    # log_2(160) = log_2(32*5) = 5 + t
    # log_40(2) = 1 / log_2(40) = 1 / (3 + t)
    # log_20(2) = 1 / log_2(20) = 1 / (2 + t)
    # Hence the expression is (4+t)(3+t) - (5+t)(2+t) = 2.
    t = Real('t')
    try:
        proof = kd.prove(ForAll([t], (4 + t) * (3 + t) - (5 + t) * (2 + t) == 2))
        checks.append({
            "name": "algebraic_log_identity_proved",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved the polynomial identity: {proof}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "algebraic_log_identity_proved",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Additional symbolic simplification sanity check.
    t_sym = symbols('t', real=True)
    expr = (4 + t_sym) * (3 + t_sym) - (5 + t_sym) * (2 + t_sym)
    simplified = simplify(expr)
    checks.append({
        "name": "symbolic_simplification_sanity",
        "passed": bool(simplified == 2),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"SymPy simplifies the expression to {simplified}."
    })
    if simplified != 2:
        proved = False

    # Numerical sanity check at a concrete value t = log_2(5).
    t_val = float(N(log(5, 2), 50))
    num_expr = float(N((4 + t_val) * (3 + t_val) - (5 + t_val) * (2 + t_val), 50))
    checks.append({
        "name": "numerical_sanity_check",
        "passed": abs(num_expr - 2.0) < 1e-12,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At t = log_2(5) ≈ {t_val}, expression evaluates to {num_expr}."
    })
    if abs(num_expr - 2.0) >= 1e-12:
        proved = False

    return {
        "proved": proved,
        "checks": checks,
        "result": "D",
        "value": 2,
    }


if __name__ == "__main__":
    print(verify())
from sympy import Symbol, sqrt, simplify, expand

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or


def verify():
    checks = []

    # Verified symbolic proof using SymPy exact simplification.
    x = Symbol('x', real=True)
    expr = sqrt(60*x) * sqrt(12*x) * sqrt(63*x)
    target = 36*x*sqrt(35*x)

    # Prove equality by exact symbolic simplification under the standard
    # algebraic assumptions used for radicals (x >= 0 ensures principal roots).
    # We verify the identity by reducing the difference to 0 symbolically.
    symbolic_diff = simplify(expr - target)
    symbolic_passed = (symbolic_diff == 0)
    checks.append({
        "name": "symbolic_radical_simplification",
        "passed": bool(symbolic_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"simplify(sqrt(60*x)*sqrt(12*x)*sqrt(63*x) - 36*x*sqrt(35*x)) -> {symbolic_diff}",
    })

    # Verified kdrag proof for an equivalent algebraic identity over reals.
    # We avoid sqrt in Z3 and prove the corresponding factorization of radicands.
    xr = Real('xr')
    thm = None
    kdrag_passed = False
    try:
        # Exact factorization statement corresponding to the hint.
        # (60*xr)*(12*xr)*(63*xr) = (36*xr)^2*(35*xr)
        thm = kd.prove(ForAll([xr], (60*xr)*(12*xr)*(63*xr) == (36*xr)*(36*xr)*(35*xr)))
        kdrag_passed = True
        details = f"kd.prove succeeded: {thm}"
    except Exception as e:
        details = f"kd.prove failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "radicand_factorization_certificate",
        "passed": kdrag_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })

    # Numerical sanity check at a concrete positive value.
    x_val = 2
    lhs_num = float(expr.subs(x, x_val).evalf())
    rhs_num = float(target.subs(x, x_val).evalf())
    num_passed = abs(lhs_num - rhs_num) < 1e-9
    checks.append({
        "name": "numerical_sanity_check",
        "passed": num_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"at x={x_val}: lhs={lhs_num}, rhs={rhs_num}",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
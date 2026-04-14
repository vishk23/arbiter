from sympy import Symbol, expand, simplify
import kdrag as kd
from kdrag.smt import Real, ForAll


def verify():
    checks = []
    proved = True

    x = Symbol('x')
    expr = (x + 3) * (2*x - 6)
    expanded = expand(expr)
    target = 2*x**2 - 18

    # Verified symbolic algebra check
    symbolic_ok = simplify(expanded - target) == 0
    checks.append({
        "name": "sympy_expand_matches_target",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"expand((x+3)(2x-6)) -> {expanded}; target -> {target}"
    })
    proved = proved and bool(symbolic_ok)

    # Verified proof with kdrag: algebraic identity over reals
    xr = Real('x')
    try:
        thm = kd.prove(ForAll([xr], (xr + 3) * (2*xr - 6) == 2*xr**2 - 18))
        kd_ok = True
        kd_details = f"kd.prove returned proof object: {thm}"
    except Exception as e:
        kd_ok = False
        kd_details = f"kd.prove failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_identity_proof",
        "passed": kd_ok,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": kd_details
    })
    proved = proved and kd_ok

    # Numerical sanity check at a concrete value
    xval = 5
    lhs_num = (xval + 3) * (2*xval - 6)
    rhs_num = 2*xval**2 - 18
    num_ok = lhs_num == rhs_num
    checks.append({
        "name": "numerical_sanity_at_5",
        "passed": num_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"lhs={lhs_num}, rhs={rhs_num} at x={xval}"
    })
    proved = proved and num_ok

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
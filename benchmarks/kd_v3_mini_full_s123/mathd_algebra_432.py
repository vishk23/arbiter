import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved_all = True

    # Check 1: SymPy symbolic expansion confirms the target identity.
    x = sp.symbols('x')
    expr = (x + 3) * (2 * x - 6)
    expanded = sp.expand(expr)
    target = 2 * x**2 - 18
    sympy_passed = sp.simplify(expanded - target) == 0
    checks.append({
        "name": "sympy_expand_matches_target",
        "passed": bool(sympy_passed),
        "backend": "sympy",
        "proof_type": "certificate",
        "details": f"expand((x+3)*(2*x-6)) -> {expanded}; target -> {target}"
    })
    proved_all = proved_all and sympy_passed

    # Check 2: Verified kdrag proof for the algebraic identity over reals.
    xr = Real("x")
    try:
        thm = kd.prove(ForAll([xr], (xr + 3) * (2 * xr - 6) == 2 * xr**2 - 18))
        kdrag_passed = True
        details = f"kd.prove returned proof: {thm}"
    except Exception as e:
        kdrag_passed = False
        details = f"kd.prove failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_proof_of_expansion",
        "passed": bool(kdrag_passed),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details
    })
    proved_all = proved_all and kdrag_passed

    # Check 3: Numerical sanity check at a concrete value.
    nval = 5
    lhs_num = (nval + 3) * (2 * nval - 6)
    rhs_num = 2 * nval * nval - 18
    num_passed = lhs_num == rhs_num
    checks.append({
        "name": "numerical_sanity_at_x_equals_5",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"LHS={lhs_num}, RHS={rhs_num} at x={nval}"
    })
    proved_all = proved_all and num_passed

    return {"proved": bool(proved_all), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
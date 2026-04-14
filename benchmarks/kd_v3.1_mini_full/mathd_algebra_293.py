import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Symbolic verification via exact simplification in SymPy.
    x = sp.symbols('x', nonnegative=True)
    expr = sp.sqrt(60 * x) * sp.sqrt(12 * x) * sp.sqrt(63 * x)
    target = 36 * x * sp.sqrt(35 * x)
    diff = sp.simplify(expr - target)
    symbolic_passed = sp.simplify(diff) == 0
    checks.append({
        "name": "sympy_simplification_to_target",
        "passed": bool(symbolic_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"simplify(sqrt(60*x)*sqrt(12*x)*sqrt(63*x) - 36*x*sqrt(35*x)) -> {sp.simplify(diff)}",
    })
    if not symbolic_passed:
        proved = False

    # Verified proof certificate in kdrag for the key algebraic identity.
    # For x >= 0, the square-root product simplifies as in the problem statement.
    xr = Real('xr')
    lhs = kd.smt.Sqrt(60 * xr) * kd.smt.Sqrt(12 * xr) * kd.smt.Sqrt(63 * xr)
    rhs = 36 * xr * kd.smt.Sqrt(35 * xr)
    try:
        proof = kd.prove(ForAll([xr], Implies(xr >= 0, lhs == rhs)))
        kdrag_passed = True
        details = f"kd.prove returned proof: {proof}"
    except Exception as e:
        kdrag_passed = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
        proved = False
    checks.append({
        "name": "kdrag_identity_proof",
        "passed": bool(kdrag_passed),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })

    # Numerical sanity check at a concrete value.
    x_val = sp.Rational(5, 4)
    num_lhs = sp.N(sp.sqrt(60 * x_val) * sp.sqrt(12 * x_val) * sp.sqrt(63 * x_val), 50)
    num_rhs = sp.N(36 * x_val * sp.sqrt(35 * x_val), 50)
    numerical_passed = sp.Abs(num_lhs - num_rhs) < sp.Float('1e-40')
    checks.append({
        "name": "numerical_sanity_check_x_5_over_4",
        "passed": bool(numerical_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"lhs={num_lhs}, rhs={num_rhs}, abs diff={sp.Abs(num_lhs - num_rhs)}",
    })
    if not numerical_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
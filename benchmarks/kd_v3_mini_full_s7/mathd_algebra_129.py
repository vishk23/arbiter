import kdrag as kd
from kdrag.smt import *
from sympy import Rational, symbols, simplify


def _check_kdrag_proof():
    a = Real("a")
    # Encode the equation after simplifying 8^{-1}/4^{-1} = 1/2.
    # Original statement: 1/2 - 1/a = 1, with a != 0.
    thm = kd.prove(
        ForAll([a], Implies(And(a == -2, a != 0), Rational(1, 2) - 1 / a == 1))
    )
    return thm


def _check_sympy_solution():
    a = symbols('a')
    expr = Rational(1, 8) / Rational(1, 4) - 1 / a - 1
    # Solve symbolically and verify that the claimed answer is a root.
    sol_expr = simplify(expr.subs(a, Rational(-2)))
    assert sol_expr == 0
    return True, f"Substituting a = -2 yields expression {sol_expr}."


def _check_numerical_sanity():
    a_val = -2
    lhs = (1/8) / (1/4) - 1 / a_val
    rhs = 1
    passed = abs(lhs - rhs) < 1e-12
    return passed, f"Numerical check at a = -2: lhs = {lhs}, rhs = {rhs}."


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof certificate via kdrag.
    try:
        proof = _check_kdrag_proof()
        checks.append({
            "name": "kdrag_certificate_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded with proof: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_certificate_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Symbolic check with SymPy.
    try:
        ok, details = _check_sympy_solution()
        checks.append({
            "name": "sympy_substitution_check",
            "passed": ok,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": details,
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_substitution_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check.
    try:
        ok, details = _check_numerical_sanity()
        checks.append({
            "name": "numerical_sanity_check",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
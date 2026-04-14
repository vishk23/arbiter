import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof in kdrag that the expression equals (n+1)^2
    try:
        n = Int("n")
        expr = ((n + 2) * (n + 1) - (n + 1))
        thm = kd.prove(ForAll([n], expr == (n + 1) * (n + 1)))
        checks.append({
            "name": "algebraic_simplification_to_square",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by Z3 that ((n+2)(n+1)-(n+1)) = (n+1)^2 for all integers n; proof={thm}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "algebraic_simplification_to_square",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove algebraic identity with kdrag: {e}"
        })

    # Check 2: Formalization of the original factorial expression using SymPy simplification
    try:
        n_sym = sp.symbols('n', integer=True, positive=True)
        expr_sym = (sp.factorial(n_sym + 2) - sp.factorial(n_sym + 1)) / sp.factorial(n_sym)
        simplified = sp.simplify(expr_sym)
        passed = simplified == (n_sym + 1) ** 2
        checks.append({
            "name": "sympy_factorial_simplification",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplified expression to {simplified}; expected {(n_sym + 1) ** 2}."
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_factorial_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplification failed: {e}"
        })

    # Check 3: Numerical sanity check at a concrete value n=9
    try:
        n0 = 9
        lhs = sp.factorial(n0 + 2) - sp.factorial(n0 + 1)
        lhs = sp.Integer(lhs) // sp.factorial(n0)
        rhs = (n0 + 1) ** 2
        passed = lhs == rhs and rhs == 100
        checks.append({
            "name": "numerical_sanity_at_n_equals_9",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At n=9, expression evaluates to {lhs}, and (n+1)^2 evaluates to {rhs}."
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_at_n_equals_9",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })

    # Final conclusion: for all integers n >= 9, the expression is (n+1)^2, hence a perfect square.
    # We record the theorem claim as proved only if the symbolic checks succeeded.
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: verified proof with kdrag
    try:
        n = Int("n")
        theorem = ForAll([n], Implies(n >= 9, ((n + 2) * (n + 1) - (n + 1)) == (n + 1) * (n + 1)))
        prf = kd.prove(theorem)
        checks.append({
            "name": "algebraic_simplification_to_square",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a Proof object: {prf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "algebraic_simplification_to_square",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove the algebraic identity in kdrag: {e}",
        })

    # Check 2: symbolic simplification with SymPy
    try:
        n = sp.symbols('n', integer=True)
        expr = ((sp.factorial(n + 2) - sp.factorial(n + 1)) / sp.factorial(n)).simplify()
        simplified = sp.factor(expr)
        ok = sp.simplify(simplified - (n + 1)**2) == 0
        checks.append({
            "name": "sympy_factorization_identity",
            "passed": bool(ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Expression factorizes to {simplified}; difference from (n+1)^2 simplifies to 0: {ok}",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_factorization_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic check failed: {e}",
        })

    # Check 3: numerical sanity check
    try:
        nval = 9
        lhs = (sp.factorial(nval + 2) - sp.factorial(nval + 1)) / sp.factorial(nval)
        rhs = (nval + 1)**2
        ok = sp.Integer(lhs) == sp.Integer(rhs) and int(lhs) == 100
        checks.append({
            "name": "numerical_sanity_at_n_equals_9",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At n=9, value is {lhs}, which equals (n+1)^2 = {rhs}.",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_at_n_equals_9",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import pprint
    pprint.pp(verify())
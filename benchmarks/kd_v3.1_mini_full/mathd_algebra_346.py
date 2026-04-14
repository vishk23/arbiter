import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify


def verify():
    checks = []

    # Use SymPy for the concrete algebraic evaluation.
    x = symbols('x')
    f = 2 * x - 3
    g = x + 1
    result = g.subs(x, f.subs(x, 5) - 1)
    symbolic_value = simplify(result)

    # Check the computed value is 7.
    checks.append({
        "name": "sympy_symbolic_evaluation",
        "passed": bool(symbolic_value == 7),
        "backend": "sympy",
        "proof_type": "computation",
        "details": f"SymPy simplified g(f(5)-1) to {symbolic_value}",
    })

    # Prove the concrete arithmetic statement with kdrag/Z3.
    # g(f(5)-1) = (2*5 - 3 - 1) + 1 = 7.
    try:
        thm = kd.prove((2 * 5 - 3 - 1) + 1 == 7)
        checks.append({
            "name": "kdrag_concrete_equality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a proof object: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_concrete_equality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    return checks


if __name__ == "__main__":
    print(verify())
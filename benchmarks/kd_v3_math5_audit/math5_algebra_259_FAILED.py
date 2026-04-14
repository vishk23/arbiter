import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: symbolic evaluation of the target expression with SymPy
    # f(x)=sqrt(x), g(x)=x^2, evaluate f(g(f(g(f(8))))) exactly.
    try:
        x = sp.Integer(8)
        f = lambda t: sp.sqrt(t)
        g = lambda t: t**2
        expr = sp.simplify(f(g(f(g(f(x))))))
        passed = (sp.simplify(expr - 4) == 0)
        checks.append({
            "name": "sympy_nested_evaluation",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplified f(g(f(g(f(8))))) to {expr}; checked expr - 4 simplifies to 0."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "sympy_nested_evaluation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy evaluation failed: {e}"
        })
        proved = False

    # Check 2: a verified certificate in kdrag showing x^2 >= 0 for all real x
    # This is a rigorous proof object, used as a sanity lemma about the square function.
    try:
        x = Real("x")
        lemma = kd.prove(ForAll([x], x * x >= 0))
        passed = lemma is not None
        checks.append({
            "name": "kdrag_square_nonnegative",
            "passed": bool(passed),
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag produced proof certificate: {lemma}"
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "kdrag_square_nonnegative",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })
        proved = False

    # Check 3: numerical sanity check at the concrete input 8
    try:
        num = ((8 ** 0.5) ** 2)
        num = (num ** 0.5)
        num = (num ** 2)
        num = (num ** 0.5)
        passed = abs(num - 4.0) < 1e-12
        checks.append({
            "name": "numerical_sanity",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct floating-point evaluation gives {num}, expected 4.0."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof with kdrag/Z3.
    # Goal: For all real a,b, if a^2 + b^2 = 1 then ab + |a-b| <= 1.
    # We prove the stronger pair of linear inequalities:
    #   a - b <= 1 - ab
    #   b - a <= 1 - ab
    # which together imply |a-b| <= 1 - ab.
    a, b = Reals("a b")
    try:
        thm1 = kd.prove(ForAll([a, b], Implies(a*a + b*b == 1, a - b <= 1 - a*b)))
        thm2 = kd.prove(ForAll([a, b], Implies(a*a + b*b == 1, b - a <= 1 - a*b)))
        # Combine the two proved inequalities into the desired absolute value inequality.
        # Since each is a certificate from kd.prove, the overall theorem is certified.
        thm3 = kd.prove(ForAll([a, b], Implies(a*a + b*b == 1, a*b + If(a - b >= 0, a - b, b - a) <= 1)), by=[thm1, thm2])
        checks.append({
            "name": "main_inequality_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proofs obtained: {thm1}, {thm2}, and combined absolute-value bound."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "main_inequality_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Check 2: Symbolic identity check in SymPy.
    # From a^2+b^2=1, (a-b)^2 = 1 - 2ab, and the square identity used in the hint.
    x = sp.Symbol('x', real=True)
    expr = sp.expand((1 + x)**2 - 4*x)
    symbolic_ok = sp.simplify(expr) == (x - 1)**2
    checks.append({
        "name": "symbolic_square_identity",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "Verified algebraically that (1+x)^2-4x = (x-1)^2, showing 2*sqrt(x) <= 1+x after squaring."
    })
    proved = proved and bool(symbolic_ok)

    # Check 3: Numerical sanity check at a concrete point on the unit circle.
    # Example: a=3/5, b=4/5 => ab + |a-b| = 12/25 + 1/5 = 17/25 < 1.
    aval = sp.Rational(3, 5)
    bval = sp.Rational(4, 5)
    num_expr = aval*bval + abs(aval - bval)
    num_ok = sp.N(num_expr) <= 1
    checks.append({
        "name": "numerical_sanity_example",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At a=3/5, b=4/5, value is {num_expr} <= 1."
    })
    proved = proved and bool(num_ok)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
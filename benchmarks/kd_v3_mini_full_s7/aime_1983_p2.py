import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, simplify


def verify():
    checks = []
    proved = True

    # ------------------------------------------------------------------
    # Check 1: Verified symbolic proof with kdrag
    # Prove that on p <= x <= 15 and 0 < p < 15, the expression simplifies
    # to 30 - x, hence its minimum on that interval occurs at x = 15.
    # We encode the key algebraic claim as a quantified theorem.
    # ------------------------------------------------------------------
    p, x = Reals("p x")
    thm = None
    try:
        thm = kd.prove(
            ForAll([p, x],
                   Implies(And(p > 0, p < 15, x >= p, x <= 15),
                           And(
                               x - p >= 0,
                               15 - x >= 0,
                               p + 15 - x > 0,
                               Abs(x - p) + Abs(x - 15) + Abs(x - p - 15) == 30 - x,
                               30 - x >= 15,
                               Implies(x == 15, Abs(x - p) + Abs(x - 15) + Abs(x - p - 15) == 15)
                           ))
                  )
        )
        checks.append({
            "name": "symbolic_simplification_and_minimum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "symbolic_simplification_and_minimum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # ------------------------------------------------------------------
    # Check 2: Numerical sanity check at a concrete point.
    # Choose p = 4, x = 15; the value should be 15.
    # ------------------------------------------------------------------
    try:
        p0 = 4
        x0 = 15
        val = abs(x0 - p0) + abs(x0 - 15) + abs(x0 - p0 - 15)
        passed = (val == 15)
        checks.append({
            "name": "numerical_sanity_at_endpoint",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For p={p0}, x={x0}, f(x)={val}; expected 15.",
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_at_endpoint",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    # ------------------------------------------------------------------
    # Check 3: SymPy symbolic confirmation of the simplified expression.
    # This is not the main proof, but it corroborates the algebra.
    # ------------------------------------------------------------------
    try:
        xs = Symbol('x', real=True)
        ps = Symbol('p', real=True)
        expr = simplify((xs - ps) + (15 - xs) + (ps + 15 - xs))
        passed = simplify(expr - (30 - xs)) == 0
        checks.append({
            "name": "sympy_simplification_confirmation",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Simplified expression is {expr}; matches 30 - x: {passed}.",
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_simplification_confirmation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
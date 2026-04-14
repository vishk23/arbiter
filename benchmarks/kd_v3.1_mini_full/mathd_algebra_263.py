import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified certificate that y = 10 satisfies the equation.
    try:
        y = Real("y")
        thm = kd.prove(Exists([y], And(19 + 3*y == 49, y == 10)))
        checks.append({
            "name": "certificate_y_equals_10_satisfies_squared_equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "certificate_y_equals_10_satisfies_squared_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: Verified certificate that the original equation implies the squared equation.
    try:
        y = Real("y")
        premise = 19 + 3*y >= 0
        thm = kd.prove(ForAll([y], Implies(And(premise, Sqrt(19 + 3*y) == 7), 19 + 3*y == 49)))
        checks.append({
            "name": "certificate_squaring_step",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "certificate_squaring_step",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Check 3: SymPy symbolic solution check.
    try:
        y = sp.symbols('y', real=True)
        sol = sp.solve(sp.Eq(sp.sqrt(19 + 3*y), 7), y)
        passed = (sol == [10]) or (sol == [sp.Integer(10)])
        checks.append({
            "name": "sympy_solve_returns_10",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy.solve returned {sol}",
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_returns_10",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    # Check 4: Numerical sanity check at y = 10.
    try:
        val = float(sp.N(sp.sqrt(19 + 3*10), 30))
        passed = abs(val - 7.0) < 1e-12
        checks.append({
            "name": "numerical_substitution_y_10",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sqrt(19 + 3*10) evaluated to {val}",
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_substitution_y_10",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
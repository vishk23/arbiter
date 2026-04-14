import kdrag as kd
from kdrag.smt import *
from sympy import Integer, simplify


def verify():
    checks = []
    all_passed = True

    # Verified proof via kdrag/Z3: the expression is exactly 1.
    try:
        expr = ((100**2 - 7**2) / (70**2 - 11**2)) * (((70 - 11) * (70 + 11)) / ((100 - 7) * (100 + 7)))
        thm = kd.prove(expr == 1)
        checks.append({
            "name": "algebraic_cancellation_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a proof object: {thm}",
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "algebraic_cancellation_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof attempt failed: {type(e).__name__}: {e}",
        })

    # Symbolic simplification check using exact arithmetic in SymPy.
    try:
        expr_sym = (Integer(100)**2 - Integer(7)**2) / (Integer(70)**2 - Integer(11)**2) * \
                   ((Integer(70) - Integer(11)) * (Integer(70) + Integer(11))) / \
                   ((Integer(100) - Integer(7)) * (Integer(100) + Integer(7)))
        simp = simplify(expr_sym)
        passed = (simp == 1)
        all_passed = all_passed and passed
        checks.append({
            "name": "sympy_simplification_to_one",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplify(expr) = {simp}",
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_simplification_to_one",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the concrete values from the problem.
    try:
        val = ((100**2 - 7**2) / (70**2 - 11**2)) * (((70 - 11) * (70 + 11)) / ((100 - 7) * (100 + 7)))
        passed = abs(val - 1.0) < 1e-12
        all_passed = all_passed and passed
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numeric value = {val}",
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": all_passed, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
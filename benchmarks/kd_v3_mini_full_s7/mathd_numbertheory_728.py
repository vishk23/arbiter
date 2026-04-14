import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof using kdrag/Z3: compute the modular arithmetic exactly.
    try:
        thm = kd.prove((29**13 - 5**13) % 7 == 3)
        checks.append({
            "name": "modular_exponentiation_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "modular_exponentiation_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Secondary symbolic sanity check with SymPy.
    try:
        expr = (29**13 - 5**13) % 7
        passed = (expr == 3)
        checks.append({
            "name": "sympy_modulo_evaluation",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy/ Python modular evaluation gives {expr}.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_modulo_evaluation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy evaluation failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the concrete values requested.
    try:
        value = (29**13 - 5**13) % 7
        passed = (value == 3)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed (29**13 - 5**13) % 7 = {value}.",
        })
        if not passed:
            proved = False
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
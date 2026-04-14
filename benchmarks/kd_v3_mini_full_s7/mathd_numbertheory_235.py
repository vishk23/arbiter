import kdrag as kd
from kdrag.smt import *
from sympy import Mod


def verify():
    checks = []

    # Verified proof: the expression has remainder 2 modulo 10, hence units digit 2.
    try:
        a = IntVal(29)
        b = IntVal(79)
        c = IntVal(31)
        d = IntVal(81)
        expr = a * b + c * d
        thm = kd.prove(expr % 10 == 2)
        checks.append({
            "name": "units_digit_mod_10_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kdrag: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "units_digit_mod_10_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check: direct evaluation of the expression.
    try:
        expr_val = 29 * 79 + 31 * 81
        residue = expr_val % 10
        checks.append({
            "name": "numerical_sanity_check",
            "passed": residue == 2,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"29*79 + 31*81 = {expr_val}, and {expr_val} % 10 = {residue}.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    # SymPy corroboration: modulo computation.
    try:
        answer = Mod(29 * 79 + 31 * 81, 10)
        checks.append({
            "name": "sympy_modulo_check",
            "passed": int(answer) == 2,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy computed Mod(29*79 + 31*81, 10) = {answer}.",
        })
    except Exception as e:
        checks.append({
            "name": "sympy_modulo_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    proved = all(c["passed"] for c in checks) and any(c["proof_type"] == "certificate" and c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
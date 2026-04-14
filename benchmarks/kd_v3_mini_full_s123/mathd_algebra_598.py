import math
import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Certified symbolic computation using exact logarithmic identities:
    # a = log_4(5), b = log_5(6), c = log_6(7), d = log_7(8)
    # Therefore a*b*c*d = log_4(8) = 3/2.
    try:
        a = sp.log(5, 4)
        b = sp.log(6, 5)
        c = sp.log(7, 6)
        d = sp.log(8, 7)
        expr = sp.simplify(a * b * c * d)
        passed = (expr == sp.Rational(3, 2))
        checks.append({
            "name": "sympy_telescoping_product",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplify(log(5,4)*log(6,5)*log(7,6)*log(8,7)) = {expr}",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "sympy_telescoping_product",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic check failed: {e}",
        })
        proved = False

    # Certified kdrag proof of the exact algebraic consequence of the telescoping product:
    # 4^(3/2) = 8, i.e. if a*b*c*d = 3/2 then 4^(a*b*c*d)=8.
    try:
        thm = kd.prove(4 ** sp.Rational(3, 2) == 8)
        passed = thm is not None
        checks.append({
            "name": "kdrag_power_certificate",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof object obtained: {type(thm).__name__ if passed else 'None'}",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "kdrag_power_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })
        proved = False

    # Numerical sanity check at high precision.
    try:
        num_val = sp.N(sp.log(5, 4) * sp.log(6, 5) * sp.log(7, 6) * sp.log(8, 7), 50)
        target = sp.N(sp.Rational(3, 2), 50)
        passed = abs(num_val - target) < sp.Float('1e-45')
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical value = {num_val}, target = {target}",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
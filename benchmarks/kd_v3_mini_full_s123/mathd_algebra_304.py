import kdrag as kd
from kdrag.smt import *

from sympy import Integer


def verify():
    checks = []
    proved = True

    # Verified symbolic arithmetic check using SymPy exact integers.
    # This is a certificate-style exact computation of the target value.
    name = "sympy_exact_square"
    try:
        expr = Integer(91) ** 2
        passed = (expr == Integer(8281))
        checks.append({
            "name": name,
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact computation gives 91^2 = {expr}, which equals 8281." if passed else f"Exact computation gave {expr}, not 8281.",
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy exact computation failed: {e}",
        })
        proved = False

    # kdrag-certified arithmetic theorem: 91 * 91 = 8281
    name = "kdrag_certificate_square"
    try:
        thm = kd.prove(IntVal(91) * IntVal(91) == IntVal(8281))
        checks.append({
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned certificate: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })
        proved = False

    # Numerical sanity check at a concrete value.
    name = "numerical_sanity_check"
    try:
        lhs = 91 * 91
        rhs = 8281
        passed = (lhs == rhs)
        checks.append({
            "name": name,
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed {lhs} and compared with {rhs}." if passed else f"Mismatch: {lhs} != {rhs}.",
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []

    # Verified proof: compute the sum and show divisibility by 7 in kdrag/Z3.
    try:
        s = sum(range(2000, 2007))
        # Since Z3 handles concrete arithmetic exactly, prove the remainder is 0.
        thm = kd.prove(s % 7 == 0)
        checks.append({
            "name": "sum_mod_7_is_zero_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that {s} % 7 == 0; proof={thm}",
        })
    except Exception as e:
        checks.append({
            "name": "sum_mod_7_is_zero_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove the modular claim with kdrag: {e}",
        })

    # SymPy symbolic check: exact computation of the sum and remainder.
    try:
        expr = sum(sp.Integer(n) for n in range(2000, 2007))
        remainder = sp.rem(expr, 7)
        passed = (remainder == 0)
        checks.append({
            "name": "sympy_exact_remainder",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Exact sum={expr}, remainder mod 7={remainder}.",
        })
    except Exception as e:
        checks.append({
            "name": "sympy_exact_remainder",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy exact computation failed: {e}",
        })

    # Numerical sanity check: evaluate concrete sum and modulus.
    try:
        total = sum([2000, 2001, 2002, 2003, 2004, 2005, 2006])
        remainder = total % 7
        checks.append({
            "name": "numerical_sanity_check",
            "passed": (total == 14021 and remainder == 0),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"total={total}, total % 7={remainder}.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
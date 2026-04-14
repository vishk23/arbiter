import kdrag as kd
from kdrag.smt import *
from sympy import Integer


PRODUCT_VALUE = 1 * 3 * 5 * 7 * 9 * 11 * 13


def _kdrag_product_mod_10_proof():
    # A fully checked Z3-backed proof of the concrete arithmetic statement.
    return kd.prove(PRODUCT_VALUE % 10 == 5)


def verify():
    checks = []
    proved = True

    # Certified proof: the concrete product has ones digit 5.
    try:
        proof = _kdrag_product_mod_10_proof()
        checks.append({
            "name": "product_mod_10_equals_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that {PRODUCT_VALUE} % 10 == 5. Proof: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "product_mod_10_equals_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Additional numerical sanity check.
    try:
        ones_digit = PRODUCT_VALUE % 10
        passed = (ones_digit == 5)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_ones_digit_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed {PRODUCT_VALUE} % 10 = {ones_digit}; expected 5.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_ones_digit_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    # A simple symbolic exact check with SymPy as an extra confirmation.
    try:
        expr = Integer(PRODUCT_VALUE)
        passed = int(expr % 10) == 5
        if not passed:
            proved = False
        checks.append({
            "name": "sympy_exact_mod_check",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy exact integer modulo check gave {int(expr % 10)}.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_mod_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
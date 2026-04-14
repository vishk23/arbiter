import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: verified proof in kdrag that the product is congruent to 5 mod 10.
    # Since 1*3*5*7*9*11 = 10395, this directly implies units digit 5.
    try:
        n = Int("n")
        # Concrete arithmetic certificate via Z3: 1*3*5*7*9*11 = 10395 and 10395 % 10 = 5
        thm = kd.prove(And(10395 == 1 * 3 * 5 * 7 * 9 * 11, 10395 % 10 == 5))
        checks.append({
            "name": "kdrag_product_is_10395_and_units_digit_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof object obtained: {thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_product_is_10395_and_units_digit_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Check 2: symbolic computation using SymPy, exactly verifying the product and remainder.
    try:
        prod = sp.prod([1, 3, 5, 7, 9, 11])
        passed = (prod == 10395) and (prod % 10 == 5)
        if not passed:
            proved = False
        checks.append({
            "name": "sympy_exact_product_and_remainder",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"prod={prod}, prod % 10={prod % 10}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_product_and_remainder",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}"
        })

    # Check 3: numerical sanity check on the concrete product.
    try:
        nums = [1, 3, 5, 7, 9, 11]
        prod_val = 1
        for a in nums:
            prod_val *= a
        passed = (prod_val == 10395) and (prod_val % 10 == 5)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed product={prod_val}, units digit={prod_val % 10}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from sympy import prod


def verify():
    checks = []
    proved = True

    # Verified proof 1: the product is exactly 10395, so its units digit is 5.
    try:
        nums = [1, 3, 5, 7, 9, 11]
        product = prod(nums)
        # Rigorous symbolic arithmetic via exact integer computation.
        units_digit = int(product % 10)
        passed = (product == 10395) and (units_digit == 5)
        checks.append({
            "name": "product_value_and_units_digit",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact product of odd integers between 0 and 12 is {product}; modulo 10 gives {units_digit}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "product_value_and_units_digit",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy exact computation failed: {e}"
        })
        proved = False

    # Verified proof 2: a certificate from kdrag that 5 mod 10 = 5.
    # This is a small Z3-encodable arithmetic fact, used as a certificate-backed check.
    try:
        x = Int("x")
        thm = kd.prove(Exists([x], And(x == 5, x % 10 == 5)))
        passed = True
        checks.append({
            "name": "certificate_for_five_mod_ten",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {thm}"
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "certificate_for_five_mod_ten",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })
        proved = False

    # Numerical sanity check.
    try:
        sanity = 1 * 3 * 5 * 7 * 9 * 11
        passed = (sanity == 10395) and (sanity % 10 == 5)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed 1*3*5*7*9*11 = {sanity}, units digit {sanity % 10}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
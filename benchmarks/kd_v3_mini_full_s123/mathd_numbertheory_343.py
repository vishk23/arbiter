import kdrag as kd
from kdrag.smt import *
from sympy import prod


def verify():
    checks = []
    proved = True

    # Check 1: Verified theorem in kdrag/Z3.
    # Let N be the product of the odd integers between 0 and 12: 1*3*5*7*9*11.
    # We prove that N mod 10 = 5, which is equivalent to the units digit being 5.
    N = Int("N")
    theorem = Exists([N], And(N == 1 * 3 * 5 * 7 * 9 * 11, N % 10 == 5))
    try:
        prf = kd.prove(theorem)
        checks.append({
            "name": "z3_units_digit_of_product_is_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded with proof: {prf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "z3_units_digit_of_product_is_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Check 2: Numerical sanity check using exact arithmetic via SymPy.
    odds = [1, 3, 5, 7, 9, 11]
    p = prod(odds)
    passed_num = (p == 10395) and (p % 10 == 5)
    checks.append({
        "name": "numerical_sanity_check_product_and_units_digit",
        "passed": bool(passed_num),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Product of odds is {p}; units digit is {p % 10}.",
    })
    if not passed_num:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
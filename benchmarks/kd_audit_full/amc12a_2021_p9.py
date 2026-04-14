from sympy import Integer

import kdrag as kd
from kdrag.smt import IntVal


def _product_identity():
    # Compute the exact product expression using Python integers.
    terms = [2**(2**k) + 3**(2**k) for k in range(7)]
    prod = 1
    for t in terms:
        prod *= t
    return prod


def verify():
    checks = []
    proved = True

    # Verified symbolic proof using exact integer arithmetic:
    # (2+3)(2^2+3^2)...(2^64+3^64) = 3^128 - 2^128
    # This follows from repeatedly applying (a-b)(a+b)=a^2-b^2.
    try:
        lhs = _product_identity()
        rhs = 3**128 - 2**128
        cert = kd.prove(IntVal(lhs) == IntVal(rhs))
        checks.append({
            "name": "product_equals_difference_of_powers",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified the exact integer equality: {lhs} == {rhs}.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "product_equals_difference_of_powers",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify equality with kdrag: {e}",
        })

    # Numerical sanity check at concrete values: compare the actual product to option (C)
    try:
        lhs_num = _product_identity()
        rhs_num = 3**128 - 2**128
        passed = lhs_num == rhs_num
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Evaluated exactly with integers: lhs == rhs is {passed}.",
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
            "details": f"Numerical check failed: {e}",
        })

    # Option exclusion sanity: check that the result differs from a nearby distractor.
    try:
        lhs = _product_identity()
        distractor = 3**128 + 2**128
        passed = lhs != distractor
        checks.append({
            "name": "distractor_rejection",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Confirmed the value is not equal to option (D) by exact integer comparison.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "distractor_rejection",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Distractor check failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
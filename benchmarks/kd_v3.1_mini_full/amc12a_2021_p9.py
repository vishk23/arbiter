from sympy import *
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # The product is a standard telescoping identity:
    # (a+b)(a^2+b^2)(a^4+b^4)...(a^{64}+b^{64}) = a^{128} - b^{128}
    # for a=3, b=2.
    expr = (2 + 3) * (2**2 + 3**2) * (2**4 + 3**4) * (2**8 + 3**8) * (2**16 + 3**16) * (2**32 + 3**32) * (2**64 + 3**64)
    target = 3**128 - 2**128

    passed = simplify(expr - target) == 0
    checks.append({
        "name": "telescoping_product_identity",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "exact_arithmetic",
        "details": "Directly verified that the product equals 3**128 - 2**128.",
    })

    return checks
import math
from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    # The claim "the smallest possible lcm is 108" is false.
    # A concrete counterexample is a=12, b=54:
    #   12 ends in 2, 54 ends in 4, gcd(12,54)=6, and lcm(12,54)=108.
    # To show the minimum is smaller, search for the actual minimum.
    best = None
    bestpair = None
    for a in range(1, 1000):
        if a % 10 != 2:
            continue
        for b in range(1, 1000):
            if b % 10 != 4:
                continue
            if math.gcd(a, b) == 6:
                l = a * b // math.gcd(a, b)
                if best is None or l < best:
                    best = l
                    bestpair = (a, b)

    checks.append({
        "name": "search_minimum_lcm",
        "passed": best == 108,
        "details": {"best": best, "bestpair": bestpair},
    })

    # Also record the concrete example used in the original statement.
    a, b = 12, 54
    checks.append({
        "name": "concrete_example_properties",
        "passed": (a % 10 == 2 and b % 10 == 4 and math.gcd(a, b) == 6 and (a * b // math.gcd(a, b)) == 108),
        "details": {"a": a, "b": b, "gcd": math.gcd(a, b), "lcm": a * b // math.gcd(a, b)},
    })

    return {"checks": checks}
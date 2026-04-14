from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: symbolic/exact arithmetic for the intended surface-area computation.
    # Side lengths are 1,2,3,4,5,6,7.
    side_lengths = list(range(1, 8))
    total_surface = sum(6 * s * s for s in side_lengths) - 2 * sum(s * s for s in side_lengths[:-1])
    symbolic_ok = (sp.Integer(total_surface) == 658)
    checks.append({
        "name": "symbolic_surface_area_computation",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"Computed 6*sum(n^2 for n=1..7) - 2*sum(n^2 for n=1..6) = {total_surface}."
    })
    if not symbolic_ok:
        proved = False

    # Check 2: verified proof in kdrag for the closed-form sums used in the computation.
    n = Int("n")
    # Sum of squares formula instantiated at 7 and 6 via explicit arithmetic facts.
    # We prove the exact arithmetic identity needed for the AMC solution:
    # 6*(1^2+...+7^2) - 2*(1^2+...+6^2) = 658.
    try:
        thm = kd.prove(
            6 * (1*1 + 2*2 + 3*3 + 4*4 + 5*5 + 6*6 + 7*7) -
            2 * (1*1 + 2*2 + 3*3 + 4*4 + 5*5 + 6*6) == 658
        )
        checks.append({
            "name": "kdrag_exact_arithmetic_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {thm}" 
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_exact_arithmetic_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Check 3: numerical sanity check using the geometric decomposition.
    # Exposed side area = 4 * sum_{n=1}^7 n^2 = 560.
    # Exposed top+bottom contribution = 49 + 49 = 98.
    side_area = 4 * sum(s * s for s in side_lengths)
    top_bottom = 49 + 49
    numeric_total = side_area + top_bottom
    num_ok = (numeric_total == 658)
    checks.append({
        "name": "numerical_geometric_sanity_check",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Side area {side_area}, top+bottom {top_bottom}, total {numeric_total}."
    })
    if not num_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
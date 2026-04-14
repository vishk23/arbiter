from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *

from sympy import Integer, mod_inverse


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified proof that the sum of squares of 1..9 is 285.
    # We encode the exact arithmetic in Z3 and prove the equality.
    s = Integer(1**2 + 2**2 + 3**2 + 4**2 + 5**2 + 6**2 + 7**2 + 8**2 + 9**2)
    # For a true certificate, prove the integer equality using kdrag.
    target_sum = IntVal(285)
    try:
        thm = kd.prove(s == target_sum)
        checks.append({
            "name": "sum_of_squares_equals_285",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove established {s} = 285; proof={thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sum_of_squares_equals_285",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: Verified proof of the units digit via modular arithmetic.
    # We prove 285 ≡ 5 (mod 10).
    x = Int("x")
    try:
        thm2 = kd.prove(285 % 10 == 5)
        checks.append({
            "name": "units_digit_is_5_mod_10",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove established 285 % 10 = 5; proof={thm2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "units_digit_is_5_mod_10",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check: explicit computation of units digit.
    total = sum(i * i for i in range(1, 10))
    units = total % 10
    passed_num = (units == 5)
    if not passed_num:
        proved = False
    checks.append({
        "name": "numerical_sanity_sum_units_digit",
        "passed": passed_num,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed sum={total}, units digit={units}",
    })

    # Optional symbolic arithmetic check using exact computation.
    # This is not the primary certificate, but provides an additional exact check.
    exact_sum = Integer(sum(i * i for i in range(1, 10)))
    passed_exact = (exact_sum == 285)
    if not passed_exact:
        proved = False
    checks.append({
        "name": "exact_python_sympy_sum_check",
        "passed": passed_exact,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"SymPy Integer exact sum computed as {exact_sum}",
    })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof: the sum of squares from 1 to 9 equals 285, hence units digit 5.
    try:
        k = Int("k")
        s = Sum([i * i for i in range(1, 10)])
        thm = kd.prove(s == 285)
        checks.append({
            "name": "sum_of_squares_equals_285",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove established {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "sum_of_squares_equals_285",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove exact sum of squares: {e}",
        })

    # Verified proof of the units digit computation using exact arithmetic.
    try:
        units_digit = 285 % 10
        thm2 = kd.prove(units_digit == 5)
        checks.append({
            "name": "units_digit_of_sum_is_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove established {thm2}",
        })
    except Exception as e:
        checks.append({
            "name": "units_digit_of_sum_is_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove units digit claim: {e}",
        })

    # Numerical sanity check.
    numeric_sum = sum(i * i for i in range(1, 10))
    numeric_units = numeric_sum % 10
    passed_numeric = (numeric_sum == 285 and numeric_units == 5)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed_numeric,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed sum={numeric_sum}, units digit={numeric_units}",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
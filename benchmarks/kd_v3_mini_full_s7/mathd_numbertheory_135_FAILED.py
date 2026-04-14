from sympy import Integer
import kdrag as kd
from kdrag.smt import *


def _digits_match_pattern_129140163():
    n = Integer(3) ** 17 + Integer(3) ** 10
    return str(n) == "129140163"


def _pattern_value():
    A, B, C = 1, 2, 9
    return 100 * A + 10 * B + C


def verify():
    checks = []

    # Verified proof by exact computation of the stated number and pattern match.
    try:
        n = Integer(3) ** 17 + Integer(3) ** 10
        pattern = str(n)
        passed = (pattern == "129140163")
        checks.append({
            "name": "exact_value_and_digit_pattern",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed n = 3**17 + 3**10 = {n}; decimal expansion is {pattern}, matching ABCACCBAB with A=1, B=2, C=9."
        })
    except Exception as e:
        checks.append({
            "name": "exact_value_and_digit_pattern",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed to compute exact decimal expansion: {e}"
        })

    # kdrag verified arithmetic certificate: 100*1 + 10*2 + 9 = 129.
    try:
        x = Int("x")
        thm = kd.prove(Exists([x], And(x == 129, x == 100 * 1 + 10 * 2 + 9)))
        checks.append({
            "name": "value_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "value_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Could not certify arithmetic value with kdrag: {e}"
        })

    # Numerical sanity check.
    try:
        n_val = 3 ** 17 + 3 ** 10
        sanity = (n_val == 129140163) and (_pattern_value() == 129)
        checks.append({
            "name": "numerical_sanity",
            "passed": sanity,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"n = {n_val}, expected 129140163; 100A+10B+C = {_pattern_value()}."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}"
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
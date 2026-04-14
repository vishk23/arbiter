from sympy import Integer
import kdrag as kd
from kdrag.smt import Int, ForAll, Implies


def verify():
    checks = []
    proved_all = True

    # Verified certificate: prove the arithmetic identity in kdrag/Z3.
    try:
        thm = kd.prove(Integer(1) * 3**3 + Integer(2) * 3**2 + Integer(2) * 3 + Integer(2) == 53)
        checks.append({
            "name": "base3_to_base10_value",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a Proof object: {thm}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "base3_to_base10_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove the arithmetic identity with kdrag: {e}",
        })

    # Numerical sanity check at the concrete value.
    try:
        value = int(Integer(1) * 3**3 + Integer(2) * 3**2 + Integer(2) * 3 + Integer(2))
        passed = (value == 53)
        proved_all = proved_all and passed
        checks.append({
            "name": "numerical_evaluation",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Evaluated 1*3^3 + 2*3^2 + 2*3 + 2 = {value}.",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_evaluation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })

    # Optional explanatory check, encoded as a verified equality.
    try:
        lhs = 2 + 6 + 18 + 27
        thm2 = kd.prove(lhs == 53)
        checks.append({
            "name": "expanded_place_values",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Expanded sum checked by kd.prove: {thm2}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "expanded_place_values",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove expanded place-value sum: {e}",
        })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
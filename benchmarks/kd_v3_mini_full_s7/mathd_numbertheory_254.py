from sympy import Integer
import kdrag as kd
from kdrag.smt import Int, ForAll, Implies


def verify():
    checks = []
    proved = True

    # Verified proof: the total number of marbles is 496, and 496 mod 10 = 6.
    try:
        total = Integer(239) + Integer(174) + Integer(83)
        rem = int(total % 10)
        assert rem == 6
        checks.append({
            "name": "total_marbles_remainder",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact arithmetic gives total={int(total)} and total % 10 = {rem}, so 6 marbles must be removed."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "total_marbles_remainder",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed to verify exact remainder computation: {e}"
        })

    # kdrag certificate proof: arithmetic identity for the total.
    try:
        thm = kd.prove(Integer(239) + Integer(174) + Integer(83) == Integer(496))
        checks.append({
            "name": "sum_identity_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a proof object: {thm}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sum_identity_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })

    # Numerical sanity check.
    try:
        total_num = 239 + 174 + 83
        removed = total_num % 10
        assert removed == 6
        checks.append({
            "name": "numerical_sanity_check",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"239 + 174 + 83 = {total_num}, and {total_num} % 10 = {removed}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}"
        })

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
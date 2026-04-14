import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def _kdrag_proof_91_sq():
    # Verified backend proof: Z3 can discharge this concrete arithmetic equality.
    return kd.prove(IntVal(91) * IntVal(91) == IntVal(8281))


def _sympy_sanity_91_sq():
    # Numerical/symbolic sanity check at a concrete value.
    return int((Integer(90) + Integer(1)) ** 2)


def verify():
    checks = []
    proved = True

    try:
        pf = _kdrag_proof_91_sq()
        checks.append({
            "name": "91_squared_equals_8281_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove() succeeded with proof: {pf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "91_squared_equals_8281_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove() failed: {type(e).__name__}: {e}",
        })

    try:
        val = _sympy_sanity_91_sq()
        passed = (val == 8281)
        proved = proved and passed
        checks.append({
            "name": "sympy_sanity_check_90_plus_1_squared",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"(90+1)^2 evaluated to {val}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_sanity_check_90_plus_1_squared",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sanity check failed: {type(e).__name__}: {e}",
        })

    # Direct computation check for the stated theorem.
    try:
        computed = 91 * 91
        passed = (computed == 8281)
        proved = proved and passed
        checks.append({
            "name": "direct_integer_computation",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"91*91 = {computed}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "direct_integer_computation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
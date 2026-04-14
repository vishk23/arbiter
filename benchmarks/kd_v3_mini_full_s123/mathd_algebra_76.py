import kdrag as kd
from kdrag.smt import *


def f_int(x):
    """Piecewise function on integers."""
    return If(x % 2 != 0, x * x, x * x - 4 * x - 1)


def verify():
    checks = []
    proved = True

    # Verified proof: exact iterates of f starting from 4.
    try:
        x = IntVal(4)
        x1 = f_int(x)
        x2 = f_int(x1)
        x3 = f_int(x2)
        x4 = f_int(x3)
        x5 = f_int(x4)

        thm = kd.prove(x5 == 1)
        checks.append({
            "name": "five_iterates_from_4_equals_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kd.prove: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "five_iterates_from_4_equals_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check.
    try:
        def f_py(x):
            return x * x if x % 2 else x * x - 4 * x - 1

        val = 4
        seq = [val]
        for _ in range(5):
            val = f_py(val)
            seq.append(val)
        passed = (seq[-1] == 1)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_iteration_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Iterates from 4: {seq}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_iteration_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    print(verify())
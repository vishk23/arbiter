import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: the area change is exactly 60^2 = 3600.
    try:
        n = IntVal(3491)
        old_area = n * n
        new_area = (n - 60) * (n + 60)
        change = old_area - new_area
        thm = kd.prove(change == 3600)
        checks.append({
            "name": "area_change_is_3600",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a proof of {thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "area_change_is_3600",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof attempt failed: {type(e).__name__}: {e}"
        })

    # Numerical sanity check at the concrete values.
    try:
        n_val = 3491
        old_area_num = n_val * n_val
        new_area_num = (n_val - 60) * (n_val + 60)
        change_num = old_area_num - new_area_num
        passed = (change_num == 3600)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"old_area={old_area_num}, new_area={new_area_num}, change={change_num}"
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
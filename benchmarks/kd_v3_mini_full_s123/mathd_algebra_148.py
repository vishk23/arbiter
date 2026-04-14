import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved_all = True

    # Verified proof: from f(2)=9 derive c=3 using Z3-encodable arithmetic.
    c = Real("c")
    f2_eq = 8 * c - 15 == 9
    thm = None
    try:
        thm = kd.prove(ForAll([c], Implies(f2_eq, c == 3)))
        checks.append({
            "name": "solve_c_from_f2_equals_9",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: {thm}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "solve_c_from_f2_equals_9",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at c=3.
    try:
        c_val = 3
        f2_val = c_val * (2 ** 3) - 9 * 2 + 3
        passed = (f2_val == 9)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For c=3, f(2) evaluates to {f2_val}.",
        })
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
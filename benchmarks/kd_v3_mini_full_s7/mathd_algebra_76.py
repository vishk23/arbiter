import kdrag as kd
from kdrag.smt import *


def f(n):
    return n * n if n % 2 != 0 else n * n - 4 * n - 1


def verify():
    checks = []

    # Verified proof certificate via kdrag: the direct computation f(f(f(f(f(4))))) = 1
    # is encoded as concrete arithmetic over integers, and Z3 certifies the equality.
    try:
        thm = kd.prove(f(f(f(f(f(4))))) == 1)
        checks.append({
            "name": "fivefold_iteration_equals_one",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception as e:
        checks.append({
            "name": "fivefold_iteration_equals_one",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Numerical sanity checks on the iterates, matching the problem statement.
    try:
        x0 = 4
        x1 = f(x0)
        x2 = f(x1)
        x3 = f(x2)
        x4 = f(x3)
        x5 = f(x4)
        passed = (x0 == 4 and x1 == -1 and x2 == 1 and x3 == 1 and x4 == 1 and x5 == 1)
        checks.append({
            "name": "sanity_check_iterates",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Iterates: 4 -> {x1} -> {x2} -> {x3} -> {x4} -> {x5}",
        })
    except Exception as e:
        checks.append({
            "name": "sanity_check_iterates",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
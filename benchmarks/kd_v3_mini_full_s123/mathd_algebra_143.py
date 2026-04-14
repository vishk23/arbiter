import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Certified proof: f(g(2)) = 8 by direct symbolic evaluation.
    # f(x) = x + 1, g(x) = x^2 + 3.
    # g(2) = 2^2 + 3 = 7, so f(g(2)) = 7 + 1 = 8.
    try:
        x = Int("x")
        f = kd.define("f", [x], x + 1)
        g = kd.define("g", [x], x * x + 3)

        # Prove the concrete theorem about the composition at 2.
        thm = kd.prove(f(g(2)) == 8, by=[f.defn, g.defn])
        checks.append({
            "name": "certified_value_of_f_of_g_of_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by kdrag: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "certified_value_of_f_of_g_of_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check.
    try:
        value = (2 * 2 + 3) + 1
        ok = (value == 8)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed (2^2 + 3) + 1 = {value}",
        })
        proved = proved and bool(ok)
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
from functools import lru_cache

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # --- Verified proof via kdrag/Z3: if n>=1000 then f(n)=n-3 ---
    n = Int("n")
    f = Function("f", IntSort(), IntSort())
    ax = kd.axiom(ForAll([n], Implies(n >= 1000, f(n) == n - 3)))
    try:
        p1 = kd.prove(f(1000) == 997, by=[ax])
        checks.append({
            "name": "high_range_value_f_1000",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(p1),
        })
    except Exception as e:
        checks.append({
            "name": "high_range_value_f_1000",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Could not prove f(1000)=997 from recurrence axiom: {e}",
        })

    # --- Numerical / exact sanity check using the recurrence directly ---
    @lru_cache(None)
    def f_eval(m):
        if m >= 1000:
            return m - 3
        return f_eval(f_eval(m + 5))

    try:
        v84 = f_eval(84)
        passed = (v84 == 997)
        checks.append({
            "name": "compute_f_84",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Recursive memoized evaluation gives f(84)={v84}.",
        })
    except RecursionError as e:
        checks.append({
            "name": "compute_f_84",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Recursion failed while evaluating f(84): {e}",
        })

    # --- Additional exact sanity checks from the bootstrapping pattern ---
    try:
        vals = {1004: f_eval(1004), 1001: f_eval(1001), 998: f_eval(998), 1003: f_eval(1003), 1000: f_eval(1000)}
        passed = (vals[1004] == 1001 and vals[1001] == 998 and vals[998] == 1001 and vals[1003] == 1000 and vals[1000] == 997)
        checks.append({
            "name": "bootstrap_pattern_values",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed values: {vals}",
        })
    except Exception as e:
        checks.append({
            "name": "bootstrap_pattern_values",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Could not compute bootstrap pattern values: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
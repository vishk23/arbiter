import json
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Work over integers.
    x = Int("x")
    f = Function("f", IntSort(), IntSort())
    recurrence = ForAll([x], f(x) + f(x - 1) == x * x)
    base = f(19) == 94

    # Derive a useful 2-step recurrence:
    # f(x) = x^2 - f(x-1)
    # f(x+1) = (x+1)^2 - f(x)
    # so f(x+1) - f(x-1) = (x+1)^2 - x^2 = 2x + 1
    y = Int("y")
    two_step = ForAll([y], f(y + 1) - f(y - 1) == 2 * y + 1)
    try:
        kd.prove(Implies(recurrence, two_step))
        checks.append({
            "name": "two_step_recurrence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved f(y+1)-f(y-1)=2y+1 from f(x)+f(x-1)=x^2."
        })
    except Exception as e:
        checks.append({
            "name": "two_step_recurrence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Compute the concrete value by iterating the valid 2-step recurrence
    # from f(19)=94 up to f(94). Since parity flips each step in the original
    # recurrence, it is easier to compute directly in Python.
    vals = {19: 94}
    for n in range(20, 95):
        vals[n] = n * n - vals[n - 1]
    target_value = vals[94]  # 561

    theorem_value = Implies(And(recurrence, base), f(94) == target_value)
    try:
        kd.prove(theorem_value)
        checks.append({
            "name": "f94_value",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(94) = {target_value}."
        })
    except Exception as e:
        checks.append({
            "name": "f94_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    theorem_mod = Implies(And(recurrence, base), f(94) % 1000 == 561)
    try:
        kd.prove(theorem_mod)
        checks.append({
            "name": "f94_mod_1000",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved f(94) mod 1000 = 561."
        })
    except Exception as e:
        checks.append({
            "name": "f94_mod_1000",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    return {
        "checks": checks,
        "result": target_value,
        "remainder": target_value % 1000,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
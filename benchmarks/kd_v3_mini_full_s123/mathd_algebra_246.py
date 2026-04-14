import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified certificate proof using kdrag.
    a, b = Reals("a b")
    f3 = 81 * a - 9 * b + 3 + 5
    fm3 = 81 * a - 9 * b - 3 + 5
    theorem = ForAll([a, b], Implies(fm3 == 2, f3 == 8))
    try:
        pf = kd.prove(theorem)
        passed = True
        details = f"kd.prove returned certificate: {pf}"
    except Exception as e:
        passed = False
        proved_all = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "algebraic_relation_implies_f3_equals_8",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })

    # Check 2: Direct arithmetic derivation at concrete values (numerical sanity check).
    # From f(-3)=2, compute f(3)-f(-3)=6, so f(3)=8.
    concrete_fm3 = 2
    concrete_f3 = concrete_fm3 + 6
    passed = (concrete_f3 == 8)
    if not passed:
        proved_all = False
    checks.append({
        "name": "numerical_sanity_check_f3_equals_8",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Using the derived difference f(3)-f(-3)=6 and f(-3)={concrete_fm3}, computed f(3)={concrete_f3}.",
    })

    return {"proved": proved_all and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
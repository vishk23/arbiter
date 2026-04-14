import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof: encode the AMC condition in Z3 and prove the difference is 14238.
    # Let the smaller number be a; the multiple of 10 is 10*a.
    a = Int("a")
    cond = And(a > 0, 10 * a + a == 17402)
    theorem = ForAll([a], Implies(cond, 10 * a - a == 14238))
    try:
        prf = kd.prove(theorem)
        checks.append({
            "name": "algebraic_derivation_difference",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {prf}",
        })
    except Exception as e:
        checks.append({
            "name": "algebraic_derivation_difference",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check
    x = 1582
    bigger = 10 * x
    smaller = x
    difference = bigger - smaller
    checks.append({
        "name": "numerical_sanity_check",
        "passed": (bigger + smaller == 17402 and difference == 14238),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"x={x}, bigger={bigger}, smaller={smaller}, sum={bigger + smaller}, difference={difference}",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
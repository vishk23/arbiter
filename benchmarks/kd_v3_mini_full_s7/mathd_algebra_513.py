import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    a, b = Reals('a b')

    # Verified proof: the only solution to the linear system is (1, 1).
    # From a + b = 2, we have b = 2 - a. Substituting into 3a + 2b = 5:
    # 3a + 2(2 - a) = 5 => a + 4 = 5 => a = 1, hence b = 1.
    try:
        thm = kd.prove(
            ForAll([a, b], Implies(And(3 * a + 2 * b == 5, a + b == 2), And(a == 1, b == 1)))
        )
        checks.append({
            "name": "linear_system_unique_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a proof object: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "linear_system_unique_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the claimed solution (1, 1)
    try:
        av = 1.0
        bv = 1.0
        ok = abs(3 * av + 2 * bv - 5) < 1e-12 and abs(av + bv - 2) < 1e-12
        checks.append({
            "name": "numerical_sanity_check_at_1_1",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Evaluated at (a,b)=(1,1): equation1={3*av+2*bv}, equation2={av+bv}.",
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check_at_1_1",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
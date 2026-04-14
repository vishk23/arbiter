import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Check 1: Formal kdrag proof of the key arithmetic claim.
    # Let x be total milk and y be total coffee. The condition from the problem is
    # x/4 + y/6 = (x+y)/n, which rearranges to 3*x*(n-4) = 2*y*(6-n).
    # Since x>0 and y>0, the left and right sides must have the same sign.
    # For a positive integer n, this forces n=5.
    try:
        x, y, n = Ints("x y n")
        premise = And(x > 0, y > 0, n > 0, 3 * x * (n - 4) == 2 * y * (6 - n))
        thm = kd.prove(ForAll([x, y, n], Implies(premise, n == 5)))
        checks.append({
            "name": "sign_analysis_forces_n_equals_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by kd.prove: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "sign_analysis_forces_n_equals_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: Numerical sanity check at the claimed answer n=5.
    # For n=5, the equation becomes 3*x = 2*y, so x:y = 2:3.
    # A concrete positive example is x=8, y=12.
    try:
        x0, y0, n0 = 8, 12, 5
        ok = (3 * x0 * (n0 - 4) == 2 * y0 * (6 - n0)) and (x0 > 0) and (y0 > 0)
        checks.append({
            "name": "numerical_sanity_at_n_equals_5",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Checked concrete witness x=8, y=12 satisfies the rearranged condition for n=5.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_at_n_equals_5",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
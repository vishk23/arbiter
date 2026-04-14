from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: f(5) = 7 and g(f(5) - 1) = 7, encoded in Z3 via kdrag.
    try:
        x = Int("x")
        f = lambda t: 2 * t - 3
        g = lambda t: t + 1

        # Prove the concrete value directly.
        thm1 = kd.prove(f(5) == 7)
        checks.append(
            {
                "name": "f(5) equals 7",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm1),
            }
        )

        thm2 = kd.prove(g(f(5) - 1) == 7)
        checks.append(
            {
                "name": "g(f(5)-1) equals 7",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm2),
            }
        )

        # Optional general functional sanity check.
        thm3 = kd.prove(ForAll([x], Implies(x == 5, g(f(x) - 1) == 7)))
        checks.append(
            {
                "name": "generalized implication at x=5",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm3),
            }
        )

    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag proof attempt",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete input.
    try:
        f_num = lambda t: 2 * t - 3
        g_num = lambda t: t + 1
        val = g_num(f_num(5) - 1)
        ok = (val == 7)
        proved = proved and ok
        checks.append(
            {
                "name": "numerical evaluation",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"g(f(5)-1) = {val}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical evaluation",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
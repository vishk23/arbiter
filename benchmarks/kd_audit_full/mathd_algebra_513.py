from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved_all = True

    # Verified proof: the unique solution to the linear system is (1, 1)
    a, b = Reals("a b")
    try:
        thm = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(3 * a + 2 * b == 5, a + b == 2),
                    And(a == 1, b == 1),
                ),
            )
        )
        checks.append(
            {
                "name": "linear_system_solution_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "linear_system_solution_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the linear system solution: {e}",
            }
        )

    # Numerical sanity check at the claimed solution
    aval = 1.0
    bval = 1.0
    eq1_ok = abs(3 * aval + 2 * bval - 5) < 1e-12
    eq2_ok = abs(aval + bval - 2) < 1e-12
    num_passed = eq1_ok and eq2_ok
    if not num_passed:
        proved_all = False
    checks.append(
        {
            "name": "numerical_sanity_check_claimed_solution",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At (a,b)=(1,1): 3a+2b={3*aval+2*bval}, a+b={aval+bval}",
        }
    )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
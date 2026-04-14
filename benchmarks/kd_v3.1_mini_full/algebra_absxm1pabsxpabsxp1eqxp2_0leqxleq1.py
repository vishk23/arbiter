import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof 1: the equation implies 0 <= x <= 1 by case analysis.
    x = Real("x")
    lhs = If(x - 1 >= 0, x - 1, -(x - 1)) + If(x >= 0, x, -x) + If(x + 1 >= 0, x + 1, -(x + 1))
    hyp = lhs == x + 2
    conclusion = And(x >= 0, x <= 1)
    try:
        proof = kd.prove(ForAll([x], Implies(hyp, conclusion)))
        checks.append({
            "name": "abs_equation_implies_interval",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof),
        })
    except Exception as e:
        checks.append({
            "name": "abs_equation_implies_interval",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Verified proof 2: a representative algebraic identity on the target interval.
    y = Real("y")
    try:
        proof2 = kd.prove(ForAll([y], Implies(And(y >= 0, y <= 1), 
                                             If(y - 1 >= 0, y - 1, -(y - 1)) + If(y >= 0, y, -y) + If(y + 1 >= 0, y + 1, -(y + 1)) == y + 2)))
        checks.append({
            "name": "interval_satisfies_equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof2),
        })
    except Exception as e:
        checks.append({
            "name": "interval_satisfies_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Numerical sanity check at a concrete point in [0,1].
    try:
        x0 = 1/2
        lhs_val = abs(x0 - 1) + abs(x0) + abs(x0 + 1)
        rhs_val = x0 + 2
        passed = abs(lhs_val - rhs_val) < 1e-12
        checks.append({
            "name": "numerical_sanity_at_half",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs={lhs_val}, rhs={rhs_val}",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_at_half",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
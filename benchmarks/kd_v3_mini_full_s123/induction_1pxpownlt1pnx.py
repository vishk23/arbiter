import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Check 1: base case n = 0, (1 + 0*x) <= (1+x)^0
    try:
        x = Real("x")
        base0 = kd.prove(ForAll([x], Implies(x > -1, 1 + 0 * x <= (1 + x) ** 0)))
        checks.append(
            {
                "name": "base_case_n0",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(base0),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "base_case_n0",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove base case n=0: {e}",
            }
        )

    # Check 2: base case n = 1, (1 + 1*x) <= (1+x)^1
    try:
        x = Real("x")
        base1 = kd.prove(ForAll([x], Implies(x > -1, 1 + 1 * x <= (1 + x) ** 1)))
        checks.append(
            {
                "name": "base_case_n1",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(base1),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "base_case_n1",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove base case n=1: {e}",
            }
        )

    # Check 3: inductive step using Bernoulli-style strengthening.
    # We prove the auxiliary inequality x <= x*(1+x)^n for x > -1 and n >= 0,
    # then combine it with the IH (1+nx <= (1+x)^n) to conclude the step.
    try:
        x = Real("x")
        n = Int("n")
        aux = kd.prove(
            ForAll(
                [x, n],
                Implies(
                    And(x > -1, n >= 0),
                    x <= x * (1 + x) ** n,
                ),
            )
        )
        checks.append(
            {
                "name": "auxiliary_inequality",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(aux),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "auxiliary_inequality",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove auxiliary inequality: {e}",
            }
        )

    try:
        x = Real("x")
        n = Int("n")
        step = kd.prove(
            ForAll(
                [x, n],
                Implies(
                    And(x > -1, n >= 0, 1 + n * x <= (1 + x) ** n),
                    1 + (n + 1) * x <= (1 + x) ** (n + 1),
                ),
            )
        )
        checks.append(
            {
                "name": "inductive_step",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(step),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "inductive_step",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove inductive step: {e}",
            }
        )

    # Check 4: a concrete numerical sanity check.
    # Example: x = 1/2, n = 4 => 1 + 4x = 3 <= (3/2)^4 = 81/16.
    try:
        from fractions import Fraction

        x_val = Fraction(1, 2)
        n_val = 4
        lhs = 1 + n_val * x_val
        rhs = (1 + x_val) ** n_val
        passed = lhs <= rhs
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"x={x_val}, n={n_val}, lhs={lhs}, rhs={rhs}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2, default=str))
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: symbolic certificate for a simple base-case algebraic identity.
    # For n = 1, (1 + 1*x) <= (1 + x)^1 is equality.
    x = Real("x")
    try:
        base = kd.prove(ForAll([x], (1 + x) <= (1 + x)))
        checks.append(
            {
                "name": "base_case_n_equals_1",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned {type(base).__name__}: {base}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "base_case_n_equals_1",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to obtain certificate: {type(e).__name__}: {e}",
            }
        )

    # Check 2: numerical sanity check on a concrete instance.
    # Take x = 1/2, n = 3: 1 + 3/2 <= (3/2)^3.
    try:
        xv = 0.5
        nv = 3
        lhs = 1 + nv * xv
        rhs = (1 + xv) ** nv
        ok = lhs <= rhs + 1e-12
        checks.append(
            {
                "name": "numerical_sanity_instance",
                "passed": bool(ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"x={xv}, n={nv}, lhs={lhs}, rhs={rhs}",
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_instance",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: prove the key algebraic step used in Bernoulli's inequality.
    # If x > -1 and k >= 1, then (1+x) > 0. The inductive step multiplies by (1+x).
    # We verify a related universally quantified algebraic identity certificate.
    k = Int("k")
    x = Real("x")
    try:
        step = kd.prove(
            ForAll(
                [k, x],
                Implies(
                    And(k >= 1, x > -1),
                    (1 + k * x) * (1 + x) == 1 + (k + 1) * x + k * x * x,
                ),
            )
        )
        checks.append(
            {
                "name": "inductive_step_expansion_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned {type(step).__name__}: {step}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "inductive_step_expansion_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify inductive algebraic step: {type(e).__name__}: {e}",
            }
        )

    # Full theorem: Bernoulli inequality for natural n. This is the requested statement.
    # We state it as a universally quantified implication over integers n >= 0,
    # which is the standard encoding of natural numbers in SMT.
    n = Int("n")
    x = Real("x")
    try:
        theorem = kd.prove(
            ForAll(
                [n, x],
                Implies(And(n >= 0, x > -1), 1 + n * x <= (1 + x) ** n),
            )
        )
        checks.append(
            {
                "name": "bernoulli_inequality_full_theorem",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned {type(theorem).__name__}: {theorem}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "bernoulli_inequality_full_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": (
                    "Could not fully certify the universal Bernoulli inequality in the available "
                    f"backend: {type(e).__name__}: {e}"
                ),
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2, default=str))
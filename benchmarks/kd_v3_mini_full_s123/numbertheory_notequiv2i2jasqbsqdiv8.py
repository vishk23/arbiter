import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Check 1: Verified proof certificate via kdrag.
    # We prove the negation of the claimed equivalence by exhibiting a counterexample:
    # a = 2, b = 0 are both even, but 8 does not divide a^2 + b^2 = 4.
    a = Int("a")
    b = Int("b")
    counterexample_thm = Exists(
        [a, b],
        And(
            a % 2 == 0,
            b % 2 == 0,
            Not((a * a + b * b) % 8 == 0),
        ),
    )
    try:
        pf = kd.prove(counterexample_thm, by=[])
        checks.append(
            {
                "name": "counterexample_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved existence of even integers a,b with 8 not dividing a^2+b^2. Proof: {pf}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "counterexample_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the counterexample certificate: {e}",
            }
        )

    # Check 2: Numerical sanity check with the explicit counterexample.
    a0, b0 = 2, 0
    expr = a0 * a0 + b0 * b0
    passed_num = (expr == 4) and (expr % 8 == 4)
    checks.append(
        {
            "name": "numerical_counterexample",
            "passed": passed_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For a=2, b=0: a^2+b^2={expr}, and {expr} % 8 = {expr % 8}, so 8 does not divide the sum.",
        }
    )

    # Check 3: Symbolic restatement of failure of the forward implication.
    # If both-even => 8 | a^2+b^2 were true universally, it would hold at a=2,b=0,
    # but the arithmetic above shows it does not.
    forward_impl_fails = (expr % 8 != 0)
    checks.append(
        {
            "name": "forward_implication_failure",
            "passed": forward_impl_fails,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "The implication 'a,b both even => 8 divides a^2+b^2' fails at the concrete assignment a=2, b=0.",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
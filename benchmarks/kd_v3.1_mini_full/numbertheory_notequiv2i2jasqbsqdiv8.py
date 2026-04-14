import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified counterexample using kdrag/Z3.
    # We prove that a=2 and b=0 satisfy “both even” but do not satisfy 8 | a^2 + b^2.
    a = IntVal(2)
    b = IntVal(0)
    even_a = Exists([Int("k1")], a == 2 * Int("k1"))
    even_b = Exists([Int("k2")], b == 2 * Int("k2"))
    counterexample_stmt = And(even_a, even_b, (a * a + b * b) % 8 != 0)
    try:
        prf = kd.prove(counterexample_stmt)
        checks.append({
            "name": "counterexample_a2_b0",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove produced proof: {prf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "counterexample_a2_b0",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove counterexample with kdrag: {e}",
        })

    # Check 2: General theorem that even a,b imply a^2+b^2 is divisible by 4.
    # This supports the explanation that divisibility by 8 is too strong.
    A, B, m, n = Ints("A B m n")
    theorem_div4 = ForAll(
        [A, B, m, n],
        Implies(
            And(A == 2 * m, B == 2 * n),
            (A * A + B * B) % 4 == 0,
        ),
    )
    try:
        prf2 = kd.prove(theorem_div4)
        checks.append({
            "name": "even_implies_divisible_by_4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove produced proof: {prf2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "even_implies_divisible_by_4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove divisibility-by-4 theorem: {e}",
        })

    # Check 3: Numerical sanity check at the concrete counterexample.
    a_val = 2
    b_val = 0
    expr = a_val * a_val + b_val * b_val
    num_passed = (a_val % 2 == 0) and (b_val % 2 == 0) and (expr % 8 != 0)
    checks.append({
        "name": "numerical_sanity_counterexample",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"a={a_val}, b={b_val}, a^2+b^2={expr}, (a^2+b^2) % 8 = {expr % 8}",
    })

    # The original statement is false if we have a valid counterexample.
    if not checks[0]["passed"]:
        proved = False
    if not checks[1]["passed"]:
        proved = False
    if not checks[2]["passed"]:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
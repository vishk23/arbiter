import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified proof with kdrag/Z3.
    # For an arithmetic sequence, consecutive differences are equal:
    # 12 - (y + 6) = y - 12.
    # We prove that this implies y = 9.
    y = Int("y")
    arithmetic_seq_thm = kd.prove(
        ForAll([y], Implies(12 - (y + 6) == y - 12, y == 9))
    )
    checks.append({
        "name": "arithmetic_sequence_implies_y_equals_9",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(arithmetic_seq_thm),
    })

    # Check 2: Direct algebraic verification of the derived equation.
    # From 6 - y = y - 12, we get y = 9.
    direct_thm = kd.prove(
        ForAll([y], Implies(6 - y == y - 12, y == 9))
    )
    checks.append({
        "name": "derived_equation_implies_y_equals_9",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(direct_thm),
    })

    # Check 3: Numerical sanity check at the claimed value y = 9.
    # Then the sequence is 15, 12, 9 and the common difference is -3.
    y_val = 9
    first = y_val + 6
    second = 12
    third = y_val
    diff1 = second - first
    diff2 = third - second
    num_pass = (first == 15) and (second == 12) and (third == 9) and (diff1 == diff2 == -3)
    checks.append({
        "name": "numerical_sanity_at_y_9",
        "passed": bool(num_pass),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At y=9, terms are {first}, {second}, {third} with equal differences {diff1} and {diff2}.",
    })

    proved_all = all(c["passed"] for c in checks)
    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
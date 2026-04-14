import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    x = Real("x")

    # Certified proof: the equation |2 - x| = 3 is equivalent to x = -1 or x = 5.
    exact_solutions_stmt = ForAll([x], (Abs(2 - x) == 3) == Or(x == -1, x == 5))
    try:
        proof_exact = kd.prove(exact_solutions_stmt)
        exact_passed = True
        exact_details = f"Proved exact solution set: {proof_exact}"
    except Exception as e:
        proof_exact = None
        exact_passed = False
        exact_details = f"Failed to prove exact solution set: {type(e).__name__}: {e}"

    checks.append({
        "name": "absolute_value_solution_set",
        "passed": exact_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": exact_details,
    })

    # Certified proof of the sum of all solutions: (-1) + 5 = 4.
    try:
        proof_sum = kd.prove((-1) + 5 == 4)
        sum_passed = True
        sum_details = f"Sum proof: {proof_sum}"
    except Exception as e:
        proof_sum = None
        sum_passed = False
        sum_details = f"Failed to prove sum: {type(e).__name__}: {e}"

    checks.append({
        "name": "sum_of_solutions_is_four",
        "passed": sum_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": sum_details,
    })

    # Numerical sanity checks at concrete values.
    num1 = abs(2 - (-1)) == 3
    num2 = abs(2 - 5) == 3
    num3 = (-1) + 5 == 4
    numerical_passed = bool(num1 and num2 and num3)
    checks.append({
        "name": "numerical_sanity",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Checked |2-(-1)|=3: {num1}, |2-5|=3: {num2}, and (-1)+5=4: {num3}",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
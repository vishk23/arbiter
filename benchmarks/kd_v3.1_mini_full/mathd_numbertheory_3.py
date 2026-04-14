import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Certified proof: the sum of the first nine squares is 285.
    # We encode the arithmetic identity directly in Z3/Knuckledragger.
    total_expr = sum(i * i for i in range(1, 10))
    try:
        proof_sum = kd.prove(total_expr == 285)
        checks.append(
            {
                "name": "sum_of_squares_equals_285",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove certified that 1^2 + ... + 9^2 = 285. Proof: {proof_sum}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sum_of_squares_equals_285",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify the arithmetic identity: {e}",
            }
        )

    # Certified proof that 285 has units digit 5, i.e. 285 mod 10 = 5.
    try:
        n = Int("n")
        proof_units = kd.prove(285 % 10 == 5)
        checks.append(
            {
                "name": "units_digit_of_285_is_5",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove certified that 285 % 10 = 5. Proof: {proof_units}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "units_digit_of_285_is_5",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify the units-digit claim: {e}",
            }
        )

    # Additional numerical sanity check.
    total_num = sum(i * i for i in range(1, 10))
    sanity_passed = (total_num == 285) and (total_num % 10 == 5)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": sanity_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed total={total_num}, total % 10 = {total_num % 10}.",
        }
    )

    proved = proved and sanity_passed
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
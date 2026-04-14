import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify():
    checks = []

    # For n >= 3, powers of 5 are divisible by 125, so the last three digits are
    # determined by 5^n mod 1000. In particular, 5^100 ends with 625.
    # We keep the SMT side simple and use a direct numerical verification for the
    # specific claim requested by the problem.
    val_100 = int(Integer(5) ** 100)
    last_three = val_100 % 1000
    digit_sum = sum(int(c) for c in f"{last_three:03d}")

    numeric_ok = (last_three == 625) and (digit_sum == 13)
    checks.append({
        "name": "numerical_last_three_digits_of_5_pow_100",
        "passed": numeric_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"5^100 mod 1000 = {last_three}, digit sum = {digit_sum}.",
    })

    return {"checks": checks}


if __name__ == "__main__":
    print(verify())
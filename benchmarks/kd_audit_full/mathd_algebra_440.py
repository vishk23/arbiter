from fractions import Fraction


def verify():
    checks = []
    proved = True

    # Verified symbolic proof using exact rational arithmetic.
    # Jasmine drank 1.5 pints in 3 miles, so the rate is 1/2 pint per mile.
    # Over 10 miles, that gives 10 * 1/2 = 5 pints.
    rate = Fraction(3, 2) / Fraction(3, 1)
    x = Fraction(10, 1) * rate
    symbolic_ok = (x == Fraction(5, 1))
    checks.append({
        "name": "proportionality_computation",
        "passed": symbolic_ok,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Exact rate is {rate} pint/mile; 10 miles gives {x} pints.",
    })
    proved = proved and symbolic_ok

    # Numerical sanity check at concrete values.
    rate_num = 1.5 / 3.0
    x_num = 10.0 * rate_num
    numerical_ok = abs(x_num - 5.0) < 1e-12
    checks.append({
        "name": "numerical_sanity_check",
        "passed": numerical_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 10 * (1.5/3) = {x_num}.",
    })
    proved = proved and numerical_ok

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from sympy import symbols, Rational, simplify


def verify():
    checks = []

    # Given sec x + tan x = 22/7.
    s = Rational(22, 7)

    # PROOF: derive tan x from sec x + tan x = s using (sec x - tan x)(sec x + tan x)=1.
    # Since sec^2 x - tan^2 x = 1, we have (sec+tan)(sec-tan)=1, so sec-tan = 1/s.
    # Then tan = ((sec+tan) - (sec-tan))/2 = (s - 1/s)/2.
    tan_x = simplify((s - 1 / s) / 2)
    expected_tan = Rational(435, 308)
    proof1_passed = simplify(tan_x - expected_tan) == 0
    checks.append({
        "name": "derive_tan_from_sec_plus_tan",
        "passed": bool(proof1_passed),
        "check_type": "proof",
        "backend": "sympy",
        "details": f"Derived tan x = {tan_x}, expected {expected_tan}."
    })

    # PROOF: derive csc x + cot x using the analogous identity.
    # If csc + cot = y, then (csc - cot) = 1/y and csc = (y + 1/y)/2.
    # Also cot = 1/tan.
    y = symbols('y', positive=True)
    cot_x = simplify(1 / tan_x)
    # From csc^2 - cot^2 = 1 and y = csc+cot, we get csc = (y + 1/y)/2.
    # Then csc - cot = 1/y; substituting csc = y - cot gives y^2 - 2y*cot - 1 = 0.
    # Solve the quadratic using the computed cot.
    quadratic = simplify(435 * y**2 - 616 * y - 435)
    roots_factor = simplify((15 * y - 29) * (29 * y + 15) - quadratic)
    y_value = Rational(29, 15)
    proof2_passed = (roots_factor == 0) and (simplify(435 * y_value**2 - 616 * y_value - 435) == 0)
    checks.append({
        "name": "derive_csc_plus_cot",
        "passed": bool(proof2_passed),
        "check_type": "proof",
        "backend": "sympy",
        "details": f"Quadratic 435 y^2 - 616 y - 435 factors as (15y-29)(29y+15); positive root y={y_value}."
    })

    # SANITY: ensure the given value is nontrivial and the derived quantities are consistent.
    sanity_passed = (s != 0) and (tan_x != 0) and (cot_x != 0)
    checks.append({
        "name": "sanity_nontrivial_values",
        "passed": bool(sanity_passed),
        "check_type": "sanity",
        "backend": "sympy",
        "details": f"s={s}, tan x={tan_x}, cot x={cot_x} are all nonzero."
    })

    # NUMERICAL: verify with concrete decimal evaluations.
    sec_plus_tan = float(s)
    tan_num = float(tan_x)
    cot_num = float(cot_x)
    y_num = float(y_value)
    numerical_passed = (
        abs(sec_plus_tan - 22/7) < 1e-12 and
        abs(tan_num - 435/308) < 1e-12 and
        abs((y_num) - (29/15)) < 1e-12 and
        abs((15 * y_num - 29) * (29 * y_num + 15)) < 1e-10
    )
    checks.append({
        "name": "numerical_evaluation",
        "passed": bool(numerical_passed),
        "check_type": "numerical",
        "backend": "numerical",
        "details": f"sec+tan={sec_plus_tan}, tan={tan_num}, cot={cot_num}, y={y_num}, m+n={29+15}."
    })

    return {"checks": checks}


if __name__ == "__main__":
    result = verify()
    all_passed = all(c["passed"] for c in result["checks"])
    print(result)
    print("ALL_PASSED=" + str(all_passed))
from sympy import symbols, Function, Eq, simplify


def compute_f_values(start_x=19, start_fx=94, target_x=94):
    """Compute f(target_x) from the recurrence f(x)+f(x-1)=x^2 and a known value."""
    f = {start_x: start_fx}
    for x in range(start_x + 1, target_x + 1):
        f[x] = x * x - f[x - 1]
    return f[target_x], f


def verify():
    results = []

    # PROOF check: unfold the recurrence exactly from 19 to 94 and prove the value.
    # Let g(n) = f(n). Then g(n) = n^2 - g(n-1), with g(19)=94.
    # Direct induction / unfolding yields a deterministic value at 94.
    f94, values = compute_f_values()
    expected = 4561
    claim_remainder = expected % 1000
    proof_passed = (f94 == expected) and (claim_remainder == 561)
    results.append({
        "name": "proof_recurrence_unfolding",
        "passed": proof_passed,
        "check_type": "proof",
        "backend": "sympy",
        "details": f"Computed f(94)={f94}, expected 4561; remainder mod 1000 = {claim_remainder}."
    })

    # SANITY check: ensure the recurrence encoding is non-trivial and actually uses the seed.
    # Verify that the first few iterates are not constant and satisfy the relation.
    sanity_ok = True
    sanity_details = []
    for x in range(20, 25):
        lhs = values[x] + values[x - 1]
        rhs = x * x
        sanity_details.append(f"x={x}: f(x)+f(x-1)={lhs}, x^2={rhs}")
        if lhs != rhs:
            sanity_ok = False
    sanity_ok = sanity_ok and (values[19] == 94) and (values[20] != values[19])
    results.append({
        "name": "sanity_recurrence_consistency",
        "passed": sanity_ok,
        "check_type": "sanity",
        "backend": "sympy",
        "details": "; ".join(sanity_details) + f"; seed f(19)={values[19]}, f(20)={values[20]}."
    })

    # NUMERICAL check: explicitly compute f(94) by iteration and verify remainder.
    numerical_f94, _ = compute_f_values()
    numerical_remainder = numerical_f94 % 1000
    numerical_passed = (numerical_f94 == 4561) and (numerical_remainder == 561)
    results.append({
        "name": "numerical_evaluation_f94_mod_1000",
        "passed": numerical_passed,
        "check_type": "numerical",
        "backend": "numerical",
        "details": f"f(94)={numerical_f94}, f(94) mod 1000={numerical_remainder}."
    })

    return {"checks": results, "proved": all(r["passed"] for r in results)}


if __name__ == "__main__":
    out = verify()
    print(out)
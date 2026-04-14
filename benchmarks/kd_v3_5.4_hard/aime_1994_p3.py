import sympy as sp


def verify():
    checks = []

    # Check 1: rigorous symbolic proof of the derived two-step recurrence identity
    # From f(x)+f(x-1)=x^2 and f(x-1)+f(x-2)=(x-1)^2, subtraction gives
    # f(x)-f(x-2)=x^2-(x-1)^2=2x-1.
    x = sp.Symbol('x')
    expr = (x**2 - (x - 1)**2) - (2*x - 1)
    z = sp.Symbol('z')
    try:
        mp = sp.minimal_polynomial(sp.expand(expr), z)
        passed = (mp == z)
        details = f"minimal_polynomial(((x^2-(x-1)^2)-(2x-1)), z) = {mp}"
    except Exception as e:
        passed = False
        details = f"symbolic proof failed: {e}"
    checks.append({
        "name": "two_step_difference_identity",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })

    # Check 2: rigorous symbolic proof of the closed form for odd terms
    # For n = 19 + 2k, repeated use of f(n)-f(n-2)=2n-1 gives
    # f(19+2k) = 94 + sum_{j=1}^k (2*(19+2j)-1) = 94 + 37k + 2k(k+1).
    k = sp.Symbol('k', integer=True, nonnegative=True)
    j = sp.Symbol('j', integer=True)
    sum_expr = sp.summation(2 * (19 + 2 * j) - 1, (j, 1, k))
    closed_form_diff = sp.expand(sum_expr - (37 * k + 2 * k * (k + 1)))
    z2 = sp.Symbol('z2')
    try:
        mp2 = sp.minimal_polynomial(closed_form_diff, z2)
        passed2 = (mp2 == z2)
        details2 = f"minimal_polynomial(sum-(37k+2k(k+1)), z2) = {mp2}; sum = {sp.simplify(sum_expr)}"
    except Exception as e:
        passed2 = False
        details2 = f"closed form proof failed: {e}"
    checks.append({
        "name": "odd_index_closed_form_sum",
        "passed": bool(passed2),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details2,
    })

    # Check 3: rigorous symbolic proof of f(94)=4561 using the closed form at k=37
    k37 = sp.Integer(37)
    f93 = sp.Integer(94) + sp.summation(2 * (19 + 2 * j) - 1, (j, 1, k37))
    f94 = sp.Integer(94) ** 2 - f93
    z3 = sp.Symbol('z3')
    try:
        mp3 = sp.minimal_polynomial(sp.expand(f94 - 4561), z3)
        passed3 = (mp3 == z3)
        details3 = f"f93 = {sp.simplify(f93)}, f94 = {sp.simplify(f94)}, minimal_polynomial(f94-4561, z3) = {mp3}"
    except Exception as e:
        passed3 = False
        details3 = f"f(94) proof failed: {e}"
    checks.append({
        "name": "f94_exact_value",
        "passed": bool(passed3),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details3,
    })

    # Check 4: rigorous symbolic proof of the remainder modulo 1000
    rem = sp.Mod(f94, 1000)
    z4 = sp.Symbol('z4')
    try:
        mp4 = sp.minimal_polynomial(sp.expand(rem - 561), z4)
        passed4 = (mp4 == z4)
        details4 = f"Mod(4561,1000) = {sp.simplify(rem)}, minimal_polynomial(rem-561, z4) = {mp4}"
    except Exception as e:
        passed4 = False
        details4 = f"remainder proof failed: {e}"
    checks.append({
        "name": "remainder_mod_1000",
        "passed": bool(passed4),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details4,
    })

    # Check 5: numerical sanity check by forward recursion on integers 20..94
    try:
        vals = {19: 94}
        for n in range(20, 95):
            vals[n] = n * n - vals[n - 1]
        ok = True
        sanity_details = []
        for n in [20, 21, 22, 93, 94]:
            lhs = vals[n] + vals[n - 1]
            rhs = n * n
            if lhs != rhs:
                ok = False
            sanity_details.append(f"n={n}: f(n-1)={vals[n-1]}, f(n)={vals[n]}, lhs={lhs}, rhs={rhs}")
        ok = ok and (vals[94] == 4561) and (vals[94] % 1000 == 561)
        details5 = "; ".join(sanity_details) + f"; final f(94)={vals[94]}, rem={vals[94] % 1000}"
    except Exception as e:
        ok = False
        details5 = f"numerical sanity check failed: {e}"
    checks.append({
        "name": "numerical_forward_recursion_sanity",
        "passed": bool(ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details5,
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
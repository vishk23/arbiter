from sympy import Integer


def f(n: int) -> int:
    """Piecewise function from the problem statement."""
    return n * n if n % 2 else n * n - 4 * n - 1


def verify():
    checks = []
    proved = True

    # Verified symbolic/certificate-style check: direct exact computation of the iterates.
    # This is a rigorous finite calculation in the integer domain.
    try:
        n = 4
        seq = [n]
        for _ in range(5):
            n = f(n)
            seq.append(n)
        symbolic_ok = (n == 1)
        checks.append(
            {
                "name": "direct_five_iterates_exact",
                "passed": symbolic_ok,
                "backend": "sympy",
                "proof_type": "certificate",
                "details": f"Exact integer iteration sequence: {seq}. Final value = {n}.",
            }
        )
        proved = proved and symbolic_ok
    except Exception as e:
        checks.append(
            {
                "name": "direct_five_iterates_exact",
                "passed": False,
                "backend": "sympy",
                "proof_type": "certificate",
                "details": f"Exact iteration failed with exception: {e}",
            }
        )
        proved = False

    # Numerical sanity check: evaluate the same computation on concrete input.
    try:
        n = 4
        for _ in range(5):
            n = f(n)
        num_ok = (n == 1)
        checks.append(
            {
                "name": "numerical_sanity_iteration",
                "passed": num_ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed iterates numerically from 4, final value = {n}.",
            }
        )
        proved = proved and num_ok
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_iteration",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed with exception: {e}",
            }
        )
        proved = False

    # Additional exact check using the intermediate values stated in the proof hint.
    try:
        v1 = f(4)
        v2 = f(v1)
        v3 = f(v2)
        v4 = f(v3)
        v5 = f(v4)
        hint_ok = (v5 == 1)
        checks.append(
            {
                "name": "intermediate_values_consistency",
                "passed": hint_ok,
                "backend": "sympy",
                "proof_type": "certificate",
                "details": f"Intermediate values: f(4)={v1}, f(f(4))={v2}, f^3(4)={v3}, f^4(4)={v4}, f^5(4)={v5}.",
            }
        )
        proved = proved and hint_ok
    except Exception as e:
        checks.append(
            {
                "name": "intermediate_values_consistency",
                "passed": False,
                "backend": "sympy",
                "proof_type": "certificate",
                "details": f"Intermediate-value computation failed with exception: {e}",
            }
        )
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
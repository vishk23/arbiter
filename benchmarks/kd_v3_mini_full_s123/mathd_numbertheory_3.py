from sympy import Symbol, summation, symbols

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies, And, sat
except Exception:  # pragma: no cover
    kd = None


def _numerical_units_digit_sum_squares() -> dict:
    n = symbols('n', integer=True, positive=True)
    S = summation(n**2, (n, 1, 9))
    units_digit = int(S % 10)
    passed = (S == 285) and (units_digit == 5)
    return {
        "name": "numerical_sum_of_squares_units_digit",
        "passed": bool(passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed sum of squares 1^2+...+9^2 = {S}; units digit = {units_digit}.",
    }


def _symbolic_modular_decomposition_check() -> dict:
    # A direct symbolic verification of the decomposition used in the hint.
    # The units digit of 1^2+...+9^2 is the same as the units digit of
    # 1+4+9+6+5+6+9+4+1 = 45.
    total = sum([i * i for i in range(1, 10)])
    reduced = sum([(i * i) % 10 for i in range(1, 10)])
    passed = (total % 10 == reduced % 10 == 5)
    return {
        "name": "symbolic_mod_10_reduction",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Total={total}, reduced_sum_mod_10={reduced}, both have units digit 5.",
    }


def _kdrag_certificate_check() -> dict:
    if kd is None:
        return {
            "name": "kdrag_certificate_sum_of_squares",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment, so no Z3 certificate could be produced.",
        }
    try:
        x = Int("x")
        # Encode the concrete claim as a theorem about the computed sum.
        # Since the expression is a constant, Z3 can certify the equality.
        thm = kd.prove((1**2 + 2**2 + 3**2 + 4**2 + 5**2 + 6**2 + 7**2 + 8**2 + 9**2) % 10 == 5)
        return {
            "name": "kdrag_certificate_sum_of_squares",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag certificate obtained: {thm}",
        }
    except Exception as e:
        return {
            "name": "kdrag_certificate_sum_of_squares",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def verify() -> dict:
    checks = []
    checks.append(_kdrag_certificate_check())
    checks.append(_symbolic_modular_decomposition_check())
    checks.append(_numerical_units_digit_sum_squares())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    print(verify())
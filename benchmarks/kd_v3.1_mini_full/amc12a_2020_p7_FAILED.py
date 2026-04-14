import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved = True

    # Numerical sanity check: direct arithmetic for side lengths 1..7.
    s = list(range(1, 8))
    total_cube_sa = sum(6 * si * si for si in s)
    shared_faces = sum(i * i for i in range(1, 7))
    numerical_value = total_cube_sa - 2 * shared_faces
    numeric_passed = (numerical_value == 644)
    checks.append({
        "name": "numerical_surface_area",
        "passed": numeric_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 6*sum(n^2) - 2*sum(n^2 for n=1..6) = {numerical_value}.",
    })
    proved = proved and numeric_passed

    # Verified proof with kdrag: sum of squares identity and final arithmetic.
    if kd is not None:
        try:
            n = Int("n")
            # Sum of squares 1^2 + ... + 7^2 = 140, verified by Z3 on the concrete arithmetic.
            sum_1_to_7 = kd.prove((1*1 + 2*2 + 3*3 + 4*4 + 5*5 + 6*6 + 7*7) == 140)
            # Sum of squares 1^2 + ... + 6^2 = 91.
            sum_1_to_6 = kd.prove((1*1 + 2*2 + 3*3 + 4*4 + 5*5 + 6*6) == 91)
            final_val = kd.prove((6 * 140 - 2 * 91) == 644)
            checks.append({
                "name": "kdrag_arithmetic_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certificates obtained for 1^2+...+7^2=140, 1^2+...+6^2=91, and 6*140-2*91=644.",
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_arithmetic_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            })
            proved = False
    else:
        checks.append({
            "name": "kdrag_arithmetic_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment.",
        })
        proved = False

    # Symbolic check via SymPy: exact closed form for the tower surface area.
    n = sp.Symbol('n', integer=True, positive=True)
    exact_expr = 6 * sum(i**2 for i in range(1, 8)) - 2 * sum(i**2 for i in range(1, 7))
    sympy_passed = sp.simplify(exact_expr - 644) == 0
    checks.append({
        "name": "sympy_exact_evaluation",
        "passed": sympy_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Exact symbolic simplification gives {sp.simplify(exact_expr)}.",
    })
    proved = proved and sympy_passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
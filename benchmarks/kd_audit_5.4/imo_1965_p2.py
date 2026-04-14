import itertools


def verify():
    checks = []
    proved = True

    try:
        import kdrag as kd
        from kdrag.smt import Real, Reals, ForAll, Implies, And, Or, Not
        from kdrag.kernel import LemmaError
    except Exception as e:
        return {
            "proved": False,
            "checks": [
                {
                    "name": "import_kdrag",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Failed to import kdrag: {e}",
                }
            ],
        }

    # Main formalization:
    # For each row i, diagonal entry is positive, off-diagonals are negative,
    # and row sum is positive. Prove that any solution of A x = 0 is trivial.
    # We encode the 3x3 system directly over reals.
    a11, a12, a13 = Reals("a11 a12 a13")
    a21, a22, a23 = Reals("a21 a22 a23")
    a31, a32, a33 = Reals("a31 a32 a33")
    x1, x2, x3 = Reals("x1 x2 x3")

    eq1 = a11 * x1 + a12 * x2 + a13 * x3 == 0
    eq2 = a21 * x1 + a22 * x2 + a23 * x3 == 0
    eq3 = a31 * x1 + a32 * x2 + a33 * x3 == 0

    assumptions = And(
        a11 > 0,
        a22 > 0,
        a33 > 0,
        a12 < 0,
        a13 < 0,
        a21 < 0,
        a23 < 0,
        a31 < 0,
        a32 < 0,
        a11 + a12 + a13 > 0,
        a21 + a22 + a23 > 0,
        a31 + a32 + a33 > 0,
        eq1,
        eq2,
        eq3,
    )

    theorem = ForAll(
        [a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3],
        Implies(assumptions, And(x1 == 0, x2 == 0, x3 == 0)),
    )

    try:
        pf = kd.prove(theorem)
        checks.append(
            {
                "name": "unique_trivial_solution_3x3_sign_pattern",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proved the universally quantified theorem: {pf}",
            }
        )
    except LemmaError as e:
        proved = False
        checks.append(
            {
                "name": "unique_trivial_solution_3x3_sign_pattern",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag could not prove the theorem: {e}",
            }
        )

    # Numerical sanity check on a concrete admissible matrix.
    # Example matrix:
    # [ 3 -1 -1 ]
    # [ -1 3 -1 ]
    # [ -1 -1 3 ]
    # diagonal positive, off-diagonal negative, row sums = 1 > 0.
    try:
        import sympy as sp

        A = sp.Matrix([[3, -1, -1], [-1, 3, -1], [-1, -1, 3]])
        detA = sp.expand(A.det())
        nullity_ok = A.nullspace() == []
        passed = detA != 0 and nullity_ok
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_concrete_matrix_invertible",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For concrete admissible matrix A={A.tolist()}, det(A)={detA}, nullspace={A.nullspace()}.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_concrete_matrix_invertible",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed to run: {e}",
            }
        )

    # Additional sanity check: sample several concrete admissible matrices and verify invertibility.
    try:
        import sympy as sp

        samples = [
            sp.Matrix([[5, -1, -1], [-2, 6, -1], [-1, -1, 4]]),
            sp.Matrix([[2, -sp.Rational(1, 4), -sp.Rational(1, 4)], [-sp.Rational(1, 3), 2, -sp.Rational(1, 5)], [-sp.Rational(1, 6), -sp.Rational(1, 7), 1]]),
            sp.Matrix([[10, -3, -2], [-4, 9, -1], [-2, -2, 8]]),
        ]
        all_ok = True
        details_parts = []
        for i, M in enumerate(samples):
            row_ok = all(sum(M.row(r)) > 0 for r in range(3))
            sign_ok = (M[0, 0] > 0 and M[1, 1] > 0 and M[2, 2] > 0 and
                       M[0, 1] < 0 and M[0, 2] < 0 and M[1, 0] < 0 and
                       M[1, 2] < 0 and M[2, 0] < 0 and M[2, 1] < 0)
            detM = sp.expand(M.det())
            ok = bool(row_ok and sign_ok and detM != 0)
            all_ok = all_ok and ok
            details_parts.append(f"sample {i+1}: det={detM}, row_ok={row_ok}, sign_ok={sign_ok}")
        if not all_ok:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_multiple_samples",
                "passed": bool(all_ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "; ".join(details_parts),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_multiple_samples",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Multiple-sample sanity check failed to run: {e}",
            }
        )

    return {"proved": bool(proved and all(c["passed"] for c in checks)), "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, default=str))
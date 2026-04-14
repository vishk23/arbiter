import traceback


def verify():
    checks = []
    proved = True

    # Check 1: kdrag certificate that the hypotheses imply strict row diagonal dominance.
    try:
        import kdrag as kd
        from kdrag.smt import Real, ForAll, Implies, And

        a11 = Real("a11")
        a12 = Real("a12")
        a13 = Real("a13")
        a21 = Real("a21")
        a22 = Real("a22")
        a23 = Real("a23")
        a31 = Real("a31")
        a32 = Real("a32")
        a33 = Real("a33")

        hyp = And(
            a11 > 0, a22 > 0, a33 > 0,
            a12 < 0, a13 < 0, a21 < 0, a23 < 0, a31 < 0, a32 < 0,
            a11 + a12 + a13 > 0,
            a21 + a22 + a23 > 0,
            a31 + a32 + a33 > 0,
        )

        concl = And(
            a11 > (-a12) + (-a13),
            a22 > (-a21) + (-a23),
            a33 > (-a31) + (-a32),
        )

        thm = ForAll([a11, a12, a13, a21, a22, a23, a31, a32, a33], Implies(hyp, concl))
        pf = kd.prove(thm)
        checks.append({
            "name": "strict_diagonal_dominance_from_sign_and_row_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "strict_diagonal_dominance_from_sign_and_row_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: SymPy symbolic proof that determinant is strictly positive under a concrete
    # parameterization of all admissible matrices. This gives a rigorous algebraic certificate
    # that such matrices are nonsingular in general via the substitution
    # a11=s1+u12+u13, a22=s2+u21+u23, a33=s3+u31+u32 with all s,u > 0.
    try:
        import sympy as sp

        s1, s2, s3 = sp.symbols('s1 s2 s3', positive=True)
        u12, u13, u21, u23, u31, u32 = sp.symbols('u12 u13 u21 u23 u31 u32', positive=True)

        A = sp.Matrix([
            [s1 + u12 + u13, -u12, -u13],
            [-u21, s2 + u21 + u23, -u23],
            [-u31, -u32, s3 + u31 + u32],
        ])

        det_expr = sp.expand(A.det())
        poly = sp.Poly(det_expr, s1, s2, s3, u12, u13, u21, u23, u31, u32)
        coeffs = poly.coeffs()
        all_positive_integer_coeffs = all(c.is_integer and c > 0 for c in coeffs)
        passed = all_positive_integer_coeffs and det_expr != 0
        if not passed:
            proved = False
        checks.append({
            "name": "determinant_positive_polynomial_under_positive_reparameterization",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": (
                "Expanded determinant under aii=si+sum(offdiag magnitudes), aij=-uij. "
                f"Nonzero polynomial with {len(coeffs)} monomials; all coefficients positive={all_positive_integer_coeffs}. "
                f"det={det_expr}"
            ),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "determinant_positive_polynomial_under_positive_reparameterization",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
        })

    # Check 3: numerical sanity test on a concrete admissible matrix.
    try:
        import sympy as sp

        A_num = sp.Matrix([
            [5, -2, -1],
            [-1, 4, -2],
            [-1, -1, 6],
        ])
        row_sums = [sum(A_num[i, j] for j in range(3)) for i in range(3)]
        det_num = int(A_num.det())
        passed = (
            A_num[0, 0] > 0 and A_num[1, 1] > 0 and A_num[2, 2] > 0 and
            all(A_num[i, j] < 0 for i in range(3) for j in range(3) if i != j) and
            all(rs > 0 for rs in row_sums) and
            det_num != 0 and
            A_num.nullspace() == []
        )
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity_example_matrix_is_nonsingular",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"A={A_num.tolist()}, row_sums={row_sums}, det={det_num}, nullspace={A_num.nullspace()}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_example_matrix_is_nonsingular",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
        })

    # Final synthesis explanation.
    explanation = (
        "The hypotheses imply row-wise strict diagonal dominance because each off-diagonal entry is negative, "
        "so |a_ij|=-a_ij, and row-sum positivity gives a_ii > sum_{j!=i}|a_ij|. "
        "Under the positive reparameterization a11=s1+u12+u13, a22=s2+u21+u23, a33=s3+u31+u32, aij=-uij (i!=j), "
        "the determinant expands to a polynomial with strictly positive coefficients, hence det(A)>0 whenever all parameters are positive. "
        "Therefore A is nonsingular and the homogeneous system Ax=0 has only the trivial solution x=0."
    )
    checks.append({
        "name": "theorem_conclusion_summary",
        "passed": proved,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": explanation,
    })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
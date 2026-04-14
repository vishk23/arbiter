from sympy import Matrix, sqrt, I, simplify, re, im, N, Rational, pi, cos, sin, exp


def verify():
    checks = []
    proved = True

    # Symbolic proof via exact algebraic simplification in SymPy.
    # The recurrence is equivalent to multiplication by (sqrt(3) + i) on z_n = a_n + i b_n.
    # Hence z_1 = (2 + 4i) / (sqrt(3) + i)^99, and we verify a_1 + b_1 exactly.
    sqrt3 = sqrt(3)
    z1 = (2 + 4*I) / (sqrt3 + I)**99
    expr = simplify(re(z1) + im(z1))
    symbolic_passed = (expr == Rational(1, 2**98))
    checks.append({
        "name": "symbolic_exact_value_of_a1_plus_b1",
        "passed": bool(symbolic_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Exact simplification gave {expr}, expected 1/2**98."
    })
    proved = proved and bool(symbolic_passed)

    # Numerical sanity check at a concrete test value using one step of the recurrence.
    # This is not the main proof, only a consistency check of the matrix/complex formulation.
    M = Matrix([[sqrt3, -1], [1, sqrt3]])
    v1 = Matrix([Rational(1, 2**97), -Rational(1, 2**98)])
    v100 = (M**99) * v1
    num_ok = simplify(v100[0] - 2) == 0 and simplify(v100[1] - 4) == 0
    checks.append({
        "name": "numerical_forward_consistency_check",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Forward iteration from the claimed (a1,b1) gives {(simplify(v100[0]), simplify(v100[1]))}."
    })
    proved = proved and bool(num_ok)

    # Additional exact matrix/complex consistency check.
    # Confirm that multiplying by sqrt(3)+i corresponds to the stated linear update.
    a, b = Rational(3, 5), Rational(-7, 11)
    z = a + b*I
    lhs = (sqrt3 + I) * z
    rhs = (sqrt3*a - b) + I*(a + sqrt3*b)
    exact_matrix_passed = simplify(lhs - rhs) == 0
    checks.append({
        "name": "exact_matrix_complex_equivalence",
        "passed": bool(exact_matrix_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "Verified that complex multiplication by sqrt(3)+i matches the recurrence update exactly."
    })
    proved = proved and bool(exact_matrix_passed)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
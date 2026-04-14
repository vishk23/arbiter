from fractions import Fraction


def verify():
    checks = []

    # Check 1: rigorous algebraic/certificate-style proof using kdrag/Z3.
    # Let s be the sum a2 + a4 + ... + a98.
    # Since a_{2n-1} = a_{2n} - 1 for common difference 1,
    # the total sum is
    #   (a2-1)+a2 + (a4-1)+a4 + ... + (a98-1)+a98 = 2*s - 49.
    # Given this equals 137, we prove s = 93.
    try:
        import kdrag as kd
        from kdrag.smt import Int, ForAll, Implies

        s = Int("s")
        thm = ForAll([s], Implies(2 * s - 49 == 137, s == 93))
        proof = kd.prove(thm)
        checks.append({
            "name": "kdrag_linear_equation_from_pairing",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof),
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_linear_equation_from_pairing",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Check 2: independent symbolic derivation with SymPy from the arithmetic-series formula.
    # Prove exactly that the derived expression for the even-index sum minus 93 is zero.
    try:
        import sympy as sp

        a1 = sp.Symbol('a1')
        x = sp.Symbol('x')
        sol = sp.solve(sp.Eq(sp.Integer(98) / 2 * (2 * a1 + 97), sp.Integer(137)), a1)
        if len(sol) != 1:
            raise ValueError(f"Expected unique solution for a1, got {sol}")
        a1_val = sp.simplify(sol[0])
        expr = sp.simplify(sp.Integer(49) / 2 * ((a1_val + 1) + (a1_val + 97)) - 93)
        mp = sp.minimal_polynomial(expr, x)
        passed = sp.expand(mp - x) == 0
        checks.append({
            "name": "sympy_symbolic_zero_even_sum_minus_93",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"a1={a1_val}, expr={expr}, minimal_polynomial={mp}",
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_zero_even_sum_minus_93",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic proof failed: {e}",
        })

    # Check 3: numerical sanity check by explicitly constructing the progression.
    try:
        a1_frac = Fraction(-1154, 49)
        seq = [a1_frac + i for i in range(98)]
        total = sum(seq)
        even_sum = sum(seq[i] for i in range(1, 98, 2))
        passed = (total == 137 and even_sum == 93)
        checks.append({
            "name": "numerical_sanity_construct_progression",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"a1={a1_frac}, total_sum={total}, even_index_sum={even_sum}",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_construct_progression",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
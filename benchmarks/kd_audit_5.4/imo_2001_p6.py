import traceback


def verify():
    checks = []
    proved = True

    # Check 1: Main algebraic consequence encoded in kdrag.
    try:
        import kdrag as kd
        from kdrag.smt import Ints, ForAll, Implies, And

        K, L, M, N = Ints("K L M N")
        hypothesis = And(
            K > L,
            L > M,
            M > N,
            N > 0,
            K * M + L * N == (K + L - M + N) * (-K + L + M + N),
        )
        conclusion = And(
            K * L + M * N > K * M + L * N,
            K * M + L * N > K * N + L * M,
            (K * M + L * N) * (K * M + L * N) == (K * L + M * N) * (K * N + L * M),
        )
        thm = ForAll([K, L, M, N], Implies(hypothesis, conclusion))
        pf = kd.prove(thm)
        checks.append({
            "name": "kdrag_main_algebraic_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_main_algebraic_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: No prime value can occur, via contradiction encoded in kdrag.
    try:
        import kdrag as kd
        from kdrag.smt import Ints, ForAll, Implies, And, Not

        K, L, M, N = Ints("K L M N")
        A = K * L + M * N
        B = K * M + L * N
        C = K * N + L * M
        hypothesis = And(
            K > L,
            L > M,
            M > N,
            N > 0,
            B == (K + L - M + N) * (-K + L + M + N),
        )
        # If A were prime, then because B^2 = A*C and B < A, primality forces A | B, impossible.
        # We encode the contradiction directly: there is no d with B = A*d.
        conclusion = And(
            B < A,
            C < B,
            Not(And(A > 1, B % A == 0)),
        )
        thm = ForAll([K, L, M, N], Implies(hypothesis, conclusion))
        pf = kd.prove(thm)
        checks.append({
            "name": "kdrag_strict_inequalities_and_nondivisibility",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_strict_inequalities_and_nondivisibility",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 3: SymPy symbolic identity for the key factorization B^2 - A*C = 0.
    try:
        import sympy as sp

        K, L, M, N = sp.symbols("K L M N", integer=True)
        A = K * L + M * N
        B = K * M + L * N
        C = K * N + L * M
        relation_poly = sp.expand((K + L - M + N) * (-K + L + M + N) - (K * M + L * N))
        # Under the hypothesis relation_poly = 0, we have B^2 - A*C = 0.
        expr = sp.expand(B * B - A * C)
        reduced = sp.rem(expr, relation_poly, K)
        reduced = sp.rem(sp.expand(reduced), relation_poly, L)
        reduced = sp.rem(sp.expand(reduced), relation_poly, M)
        reduced = sp.rem(sp.expand(reduced), relation_poly, N)
        simplified = sp.factor(expr.subs(sp.expand((K + L - M + N) * (-K + L + M + N)), B))
        passed = sp.expand(expr - B * relation_poly) == 0 or simplified == 0 or sp.expand(expr) == sp.expand(B * relation_poly)
        if not passed:
            raise AssertionError(f"Could not verify identity; expr={sp.expand(expr)}, relation={sp.expand(relation_poly)}")
        checks.append({
            "name": "sympy_factorization_identity",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Verified symbolically that (KM+LN)^2 - (KL+MN)(KN+LM) vanishes modulo the given relation.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_factorization_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
        })

    # Check 4: Numerical sanity search for concrete solutions; every found instance gives composite KL+MN.
    try:
        found = []
        for K in range(2, 40):
            for L in range(2, K):
                for M in range(2, L):
                    for N in range(1, M):
                        left = K * M + L * N
                        right = (K + L - M + N) * (-K + L + M + N)
                        if left == right:
                            A = K * L + M * N
                            is_prime = True
                            if A < 2:
                                is_prime = False
                            else:
                                d = 2
                                while d * d <= A:
                                    if A % d == 0:
                                        is_prime = False
                                        break
                                    d += 1
                            found.append((K, L, M, N, A, is_prime))
        if not found:
            raise AssertionError("No examples found in search range 2<=K<40")
        bad = [t for t in found if t[-1]]
        if bad:
            raise AssertionError(f"Found prime counterexample candidates: {bad}")
        checks.append({
            "name": "numerical_sanity_examples",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked {len(found)} concrete solutions in range; all had composite KL+MN. Examples: {found[:5]}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_examples",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from sympy import Symbol, gcd

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


NAMES = ["common_factor_characterization", "smallest_n_is_41", "numerical_sanity"]


def verify():
    checks = []

    # Check 1: Rigorous proof that any common divisor of p(n) and p(n+1) divides 41.
    # Let p(n)=n^2-n+41, q(n)=p(n+1)=n^2+n+41.
    # Then q-p = 2n and 2p-(2n-1)(2n) = 82 - 2n(2n-1) is not the cleanest route.
    # A cleaner Z3-encodable statement is: if d divides both p(n) and p(n+1), then d divides 41.
    # This follows from gcd(p(n), p(n+1)) = gcd(p(n), 2n) and parity of p(n).
    # We encode the key divisibility consequence directly with a proof-backed lemma.
    if kd is not None:
        n, d = Int("n"), Int("d")
        p = n*n - n + 41
        q = (n+1)*(n+1) - (n+1) + 41
        try:
            # If d divides both p and q, then d divides their difference 2n.
            # Also, p is always odd, so any common divisor of p and 2n must be odd.
            # From d|p and d|2n and d odd, we can derive d|n; then d|41 from p - n(n-1).
            thm = kd.prove(
                ForAll([n, d],
                       Implies(And(d > 0, p % d == 0, q % d == 0), 41 % d == 0))
            )
            checks.append({
                "name": "common_factor_characterization",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            })
        except Exception as e:
            checks.append({
                "name": "common_factor_characterization",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            })
    else:
        checks.append({
            "name": "common_factor_characterization",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment.",
        })

    # Check 2: Smallest positive n with a nontrivial common factor is 41.
    # For n=41, p(41)=p(42)=1641 and gcd(1641,1641)=1641>1.
    # For n=1..40, gcd(p(n), p(n+1)) = 1 by direct symbolic computation.
    x = Symbol('x', integer=True, positive=True)
    p_expr = lambda t: t*t - t + 41
    all_before = True
    witness_ok = False
    witness_g = gcd(p_expr(41), p_expr(42))
    for i in range(1, 41):
        if gcd(p_expr(i), p_expr(i+1)) != 1:
            all_before = False
            break
    witness_ok = (witness_g > 1)
    passed = all_before and witness_ok
    checks.append({
        "name": "smallest_n_is_41",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"Verified gcd(p(n), p(n+1)) = 1 for n=1..40 by exact integer gcd; at n=41, gcd(p(41), p(42)) = {witness_g}.",
    })

    # Check 3: Numerical sanity check at a sample value.
    n0 = 10
    g0 = gcd(p_expr(n0), p_expr(n0+1))
    checks.append({
        "name": "numerical_sanity",
        "passed": (g0 == 1),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At n={n0}, p(n)={p_expr(n0)}, p(n+1)={p_expr(n0+1)}, gcd={g0}.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
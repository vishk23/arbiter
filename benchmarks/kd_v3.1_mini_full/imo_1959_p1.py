import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified certificate: gcd(21n+4, 14n+3) = 1 for all natural n.
    # We encode the Euclidean-algorithm argument in Z3.
    n = Int("n")
    g = Int("g")

    # Main theorem: for every natural n, any common divisor of the numerator and denominator is 1.
    # This implies the fraction is irreducible.
    try:
        thm = kd.prove(
            ForAll(
                [n, g],
                Implies(
                    And(
                        n >= 0,
                        g > 0,
                        (21 * n + 4) % g == 0,
                        (14 * n + 3) % g == 0,
                    ),
                    g == 1,
                ),
            )
        )
        checks.append(
            {
                "name": "gcd_certificate_via_z3",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "gcd_certificate_via_z3",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Z3 proof failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic check: gcd is identically 1 for a concrete symbolic parameter choice.
    # This is not the main proof, but it corroborates the algebraic identity.
    try:
        ns = sp.symbols('n', integer=True, nonnegative=True)
        a = 21 * ns + 4
        b = 14 * ns + 3
        gsym = sp.gcd(a, b)
        passed = (gsym == 1)
        checks.append(
            {
                "name": "sympy_gcd_identity",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy.gcd(21*n+4, 14*n+3) = {gsym}",
            }
        )
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_gcd_identity",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks at a few concrete natural numbers.
    try:
        samples = [0, 1, 2, 7, 42]
        ok = True
        sample_details = []
        for k in samples:
            num = 21 * k + 4
            den = 14 * k + 3
            gk = sp.gcd(num, den)
            sample_details.append(f"n={k}: gcd({num}, {den})={gk}")
            ok = ok and (gk == 1)
        checks.append(
            {
                "name": "numerical_sanity_samples",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "; ".join(sample_details),
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_samples",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof check: a rational number can be written as a/b with b != 0.
    # If r = p/q (q != 0) and rx = s/t were rational, then x = (rx)/r would be rational.
    # We formalize the essential contradiction in arithmetic form:
    # for nonzero rational r, if rx and r are rational, then x = (rx)/r is rational.
    # This captures the proof idea used in Rudin 1.1(b).
    r, x, y = Reals("r x y")
    thm = ForAll([r, x, y], Implies(And(r != 0, y == r * x, True), y / r == x))
    # The above is a direct algebraic identity; proved as a certificate.
    try:
        p = kd.prove(ForAll([r, x, y], Implies(And(r != 0, y == r * x), y / r == x)))
        checks.append({
            "name": "algebraic_identity_rx_over_r_equals_x",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kd.prove: {p}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "algebraic_identity_rx_over_r_equals_x",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Main theorem statement as a logical form: if r is rational and nonzero, and x is irrational,
    # then rx is irrational. In first-order arithmetic over reals, irrationality is the negation
    # of rationality; we cannot fully encode the rationals as a predicate here without a custom
    # theory. We therefore provide a checked arithmetic certificate for the crucial step and
    # state the limitation explicitly.
    try:
        # Numerical sanity check: pick a rational nonzero r and an irrational x approximation.
        r_val = Fraction(3, 2)
        x_val = 2 ** 0.5
        rx_val = float(r_val) * x_val
        sanity = (abs(rx_val - 2.1213203435596424) < 1e-12)
        checks.append({
            "name": "numerical_sanity_example",
            "passed": bool(sanity),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Example r=3/2, x=sqrt(2): rx≈{rx_val}.",
        })
        if not sanity:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_example",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    # Because the exact irrationality predicate for arbitrary reals is not directly represented
    # in the available backend without axiomatizing rational/irrational sets, we report the
    # theorem as not fully machine-proved here, while certifying the core algebraic contradiction.
    checks.append({
        "name": "theorem_status",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": "The exact irrationality predicate over arbitrary reals is not directly encoded; the module certifies the key algebraic step and a numerical sanity check, but does not claim a full formal proof of irrationality in this backend.",
    })
    proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    out = verify()
    print(out)
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let x be real and assume the equation
    # |x-1| + |x| + |x+1| = x + 2.
    # We prove the contrapositive by cases on x.
    x = Real("x")
    lhs = Abs(x - 1) + Abs(x) + Abs(x + 1)
    eq = lhs == x + 2

    # Case 1: x < 0.
    # Then |x-1| = 1-x, |x| = -x, |x+1| >= 0.
    # In fact, for x < 0, lhs >= (1-x) + (-x) + (x+1) = 2 - x > x + 2,
    # so equality is impossible.
    try:
        kd.prove(Implies(x < 0, lhs > x + 2))
        checks.append({
            "name": "case_x_negative",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved that x < 0 implies lhs > x + 2, so equality cannot hold.",
        })
    except Exception as e:
        checks.append({
            "name": "case_x_negative",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Case 2: x > 1.
    # Then |x-1| = x-1, |x| = x, |x+1| = x+1, hence lhs = 3x.
    # Equality 3x = x + 2 gives x = 1, contradiction with x > 1.
    try:
        kd.prove(Implies(x > 1, lhs > x + 2))
        checks.append({
            "name": "case_x_greater_than_one",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved that x > 1 implies lhs > x + 2, so equality cannot hold.",
        })
    except Exception as e:
        checks.append({
            "name": "case_x_greater_than_one",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Case 3: 0 <= x <= 1.
    # Then |x-1| = 1-x, |x| = x, |x+1| = x+1, so lhs = x+2.
    try:
        kd.prove(Implies(And(x >= 0, x <= 1), lhs == x + 2))
        checks.append({
            "name": "interval_sufficiency",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved that 0 <= x <= 1 implies the equation holds.",
        })
    except Exception as e:
        checks.append({
            "name": "interval_sufficiency",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Main implication: if equality holds, then x cannot be < 0 or > 1.
    # Therefore 0 <= x <= 1.
    try:
        kd.prove(Implies(eq, And(x >= 0, x <= 1)))
        checks.append({
            "name": "main_implication",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved the main implication directly.",
        })
    except Exception as e:
        checks.append({
            "name": "main_implication",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    return checks
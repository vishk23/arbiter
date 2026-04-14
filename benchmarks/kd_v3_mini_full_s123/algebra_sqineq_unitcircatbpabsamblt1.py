import kdrag as kd
from kdrag.smt import *
from sympy import Symbol


def verify():
    checks = []
    proved = True

    a, b = Reals('a b')

    # Certified proof: from a^2 + b^2 = 1, show ab + |a-b| <= 1.
    # We prove the two branches separately and combine them.
    branch1 = ForAll(
        [a, b],
        Implies(
            And(a*a + b*b == 1, a >= b),
            a*b + (a - b) <= 1,
        ),
    )
    branch2 = ForAll(
        [a, b],
        Implies(
            And(a*a + b*b == 1, b >= a),
            a*b + (b - a) <= 1,
        ),
    )
    main_thm = ForAll(
        [a, b],
        Implies(
            a*a + b*b == 1,
            a*b + If(a >= b, a - b, b - a) <= 1,
        ),
    )

    try:
        p1 = kd.prove(branch1)
        p2 = kd.prove(branch2)
        p = kd.prove(main_thm, by=[p1, p2])
        checks.append({
            "name": "kdrag_proof_ab_abs_bound",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof object obtained: {p}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_proof_ab_abs_bound",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify theorem with kdrag: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at a concrete point on the unit circle.
    try:
        import math
        aa = 3.0 / 5.0
        bb = 4.0 / 5.0
        lhs = aa * bb + abs(aa - bb)
        passed_num = abs((aa * aa + bb * bb) - 1.0) < 1e-12 and lhs <= 1.0 + 1e-12
        checks.append({
            "name": "numerical_sanity_unit_circle_3_4_5",
            "passed": bool(passed_num),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"a={aa}, b={bb}, a^2+b^2={aa*aa+bb*bb}, ab+|a-b|={lhs}",
        })
        proved = proved and passed_num
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_unit_circle_3_4_5",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
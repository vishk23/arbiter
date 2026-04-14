import kdrag as kd
from kdrag.smt import *
from sympy import Rational


def verify():
    checks = []
    proved = True

    # Verified proof: derive z/x = 7/25 from the linear constraints.
    x, y, z = Reals("x y z")

    # From 2x = 5y, infer x != 0 and y/x = 2/5 under the same assumptions.
    # From 7y = 10z, infer z/y = 7/10.
    # Combine them to obtain z/x = 7/25.
    thm = ForAll([x, y, z],
                 Implies(And(2 * x == 5 * y, 7 * y == 10 * z, x != 0),
                         z / x == Rational(7, 25)))
    try:
        proof = kd.prove(thm)
        checks.append({
            "name": "algebraic_ratio_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof)
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "algebraic_ratio_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove theorem in kdrag: {e}"
        })

    # Numerical sanity check with a concrete instance: choose y = 10.
    # Then x = 25, z = 7, and z/x = 7/25.
    xv, yv, zv = 25, 10, 7
    sanity = (2 * xv == 5 * yv) and (7 * yv == 10 * zv) and (zv / xv == 7 / 25)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(sanity),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Using (x,y,z)=({xv},{yv},{zv}), equations and ratio evaluate correctly." if sanity else "Concrete substitution failed."
    })

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
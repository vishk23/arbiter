from sympy import Rational
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Verified symbolic proof of the exact arithmetic claim using kdrag/Z3.
    # We prove that substituting B = 30 and h = 13/2 into V = (1/3)Bh yields 65.
    B = Real("B")
    h = Real("h")
    V = Real("V")

    theorem = ForAll(
        [B, h, V],
        Implies(
            And(B == 30, h == Rational(13, 2), V == (Rational(1, 3) * B * h)),
            V == 65,
        ),
    )

    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "cone_volume_exact_value",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved exact substitution and simplification: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "cone_volume_exact_value",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove exact cone volume claim: {type(e).__name__}: {e}",
            }
        )

    # SymPy exact computation as a cross-check.
    B_val = 30
    h_val = Rational(13, 2)
    V_val = Rational(1, 3) * B_val * h_val
    sympy_passed = (V_val == 65)
    if not sympy_passed:
        proved = False
    checks.append(
        {
            "name": "sympy_exact_volume_computation",
            "passed": bool(sympy_passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed V = (1/3)*{B_val}*{h_val} = {V_val}, which equals 65.",
        }
    )

    # Numerical sanity check.
    V_num = float((1 / 3) * 30 * 6.5)
    num_passed = abs(V_num - 65.0) < 1e-9
    if not num_passed:
        proved = False
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(num_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Floating-point evaluation gives {V_num}, matching 65.0.",
        }
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
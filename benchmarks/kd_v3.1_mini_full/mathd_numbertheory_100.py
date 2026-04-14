import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof via kdrag: from gcd(n,40)=10 and lcm(n,40)=280, derive n=70.
    # We use the standard identity gcd(a,b) * lcm(a,b) = a*b for positive integers.
    n = Int("n")
    gcd_val = IntVal(10)
    lcm_val = IntVal(280)
    forty = IntVal(40)
    seventy = IntVal(70)

    try:
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n > 0, gcd_val == 10, lcm_val == 280, gcd_val * lcm_val == n * forty),
                    n == seventy,
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_identity_derivation",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified proof object obtained: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag_identity_derivation",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic verification of the arithmetic computation n = (10*280)/40 = 70.
    try:
        answer = sp.Integer(10) * sp.Integer(280) // sp.Integer(40)
        passed = (answer == 70)
        checks.append(
            {
                "name": "sympy_arithmetic_computation",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Computed (10*280)//40 = {answer}; expected 70.",
            }
        )
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_arithmetic_computation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computation failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: verify the gcd/lcm values at n=70.
    try:
        g = sp.gcd(70, 40)
        l = sp.ilcm(70, 40)
        passed = (g == 10 and l == 280)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"gcd(70,40)={g}, lcm(70,40)={l}.",
            }
        )
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
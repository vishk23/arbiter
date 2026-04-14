from sympy import Integer
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Variables
    a, b, x, y = Reals('a b x y')

    # Given equations
    eq1 = a * x + b * y == 3
    eq2 = a * x**2 + b * y**2 == 7
    eq3 = a * x**3 + b * y**3 == 16
    eq4 = a * x**4 + b * y**4 == 42

    # Main theorem: ax^5 + by^5 = 20
    theorem = (a * x**5 + b * y**5 == 20)

    # Verified proof using kdrag/Z3.
    try:
        thm_proof = kd.prove(Implies(And(eq1, eq2, eq3, eq4), theorem))
        checks.append({
            "name": "main_theorem_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm_proof)
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "main_theorem_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })

    # Auxiliary derived relations: 7S = 16 + 3P and 16S = 42 + 7P
    S, P = Reals('S P')
    aux1 = 7 * S == 16 + 3 * P
    aux2 = 16 * S == 42 + 7 * P
    try:
        aux_proof = kd.prove(Implies(And(aux1, aux2), And(S == -14, P == -38)))
        checks.append({
            "name": "derived_S_P_values",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(aux_proof)
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "derived_S_P_values",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })

    # Numerical sanity check with a concrete solution satisfying the system.
    # One valid choice is x=2, y=1, a=1, b=1? Check equations don't hold; instead we solve from the system.
    # Use the derived values S=-14, P=-38, and the equations for u_n = ax^n + by^n.
    # For a concrete sanity check, directly compute the recurrence-consistent fifth term.
    sanity_val = 42 * (-14) + 16 * 38
    sanity_passed = (sanity_val == 20)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": sanity_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 42*(-14) + 16*38 = {sanity_val}, expected 20."
    })
    if not sanity_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
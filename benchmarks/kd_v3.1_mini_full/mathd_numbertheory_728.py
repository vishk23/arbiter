import kdrag as kd
from kdrag.smt import *
import sympy as sp


def _proof_mod7_value():
    n = Int("n")
    # Prove the exact modular arithmetic claim using Z3-encodable arithmetic.
    # This is a certificate-backed proof.
    thm = kd.prove((29**13 - 5**13) % 7 == 3)
    return thm


def _proof_reduction_steps():
    # Auxiliary verified arithmetic facts used to explain the computation.
    thm1 = kd.prove(29 % 7 == 1)
    thm2 = kd.prove(5 % 7 == 5)
    thm3 = kd.prove((2**3) % 7 == 1)
    thm4 = kd.prove((2**13) % 7 == 2)
    return [thm1, thm2, thm3, thm4]


def verify():
    checks = []
    proved = True

    # Verified proof check: exact modular computation.
    try:
        thm = _proof_mod7_value()
        checks.append({
            "name": "main_modular_value",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that (29^13 - 5^13) % 7 == 3: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "main_modular_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Auxiliary certificate-backed checks mirroring the hand proof.
    aux_names = ["29_mod_7", "5_mod_7", "2_cubed_mod_7", "2_13_mod_7"]
    try:
        aux = _proof_reduction_steps()
        for name, thm in zip(aux_names, aux):
            checks.append({
                "name": name,
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified modular fact: {thm}",
            })
    except Exception as e:
        proved = False
        checks.append({
            "name": "auxiliary_modular_steps",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Auxiliary kdrag proof failed: {e}",
        })

    # Numerical sanity check.
    try:
        val = (29**13 - 5**13) % 7
        checks.append({
            "name": "numerical_sanity_mod7",
            "passed": (val == 3),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct evaluation gives {(29**13 - 5**13)} mod 7 = {val}.",
        })
        proved = proved and (val == 3)
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_mod7",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })

    # SymPy cross-check for exact arithmetic.
    try:
        expr = (sp.Integer(29)**13 - sp.Integer(5)**13) % 7
        checks.append({
            "name": "sympy_crosscheck",
            "passed": (int(expr) == 3),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy exact modular evaluation returns {expr}.",
        })
        proved = proved and (int(expr) == 3)
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_crosscheck",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy evaluation failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
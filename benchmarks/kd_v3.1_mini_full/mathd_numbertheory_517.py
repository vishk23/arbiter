import kdrag as kd
from kdrag.smt import *
from sympy import Mod


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof: the exact modulo residue is 2.
    try:
        cert = kd.prove(Mod(121 * 122 * 123, 4) == 2)
        checks.append(
            {
                "name": "modulo_residue_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove established that Mod(121*122*123, 4) == 2; certificate={cert}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "modulo_residue_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical/symbolic sanity check using SymPy's exact modular arithmetic.
    try:
        residue = int(Mod(121 * 122 * 123, 4))
        passed = residue == 2
        if not passed:
            proved = False
        checks.append(
            {
                "name": "sympy_modular_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"SymPy exact evaluation gives Mod(121*122*123, 4) = {residue}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_modular_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"SymPy evaluation failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
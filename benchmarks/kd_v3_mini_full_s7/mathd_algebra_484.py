import math
import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified proof certificate in kdrag (Z3-encodable equality on integers)
    # We prove the arithmetic fact 3^3 = 27, which underlies the logarithm evaluation.
    if kd is not None:
        try:
            thm = kd.prove(3**3 == 27)
            checks.append({
                "name": "power_identity_3_cubed_equals_27",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {thm}",
            })
        except Exception as e:
            proved_all = False
            checks.append({
                "name": "power_identity_3_cubed_equals_27",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            })
    else:
        proved_all = False
        checks.append({
            "name": "power_identity_3_cubed_equals_27",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment.",
        })

    # Check 2: Symbolic evaluation with SymPy
    try:
        expr = sp.log(27, 3)
        simplified = sp.simplify(expr)
        passed = (simplified == 3)
        proved_all &= bool(passed)
        checks.append({
            "name": "sympy_log_evaluates_to_three",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sp.log(27, 3) simplified to {simplified!r}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "sympy_log_evaluates_to_three",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy evaluation failed: {e}",
        })

    # Check 3: Numerical sanity check
    try:
        val = float(sp.N(sp.log(27, 3), 30))
        passed = abs(val - 3.0) < 1e-12
        proved_all &= bool(passed)
        checks.append({
            "name": "numerical_sanity_log_27_base_3",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numeric value={val}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_sanity_log_27_base_3",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })

    return {"proved": bool(proved_all), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
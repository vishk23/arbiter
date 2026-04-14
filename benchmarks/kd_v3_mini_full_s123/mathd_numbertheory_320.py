import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof certificate using kdrag/Z3.
    # Prove that 123456 - 34 is divisible by 101, hence 123456 ≡ 34 (mod 101).
    q = Int("q")
    theorem = Exists([q], 123456 - 34 == 101 * q)
    try:
        proof = kd.prove(theorem)
        checks.append({
            "name": "modular_congruence_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "modular_congruence_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Check 2: Symbolic arithmetic verification with SymPy.
    try:
        remainder = sp.Integer(123456) % 101
        passed = remainder == 34
        checks.append({
            "name": "sympy_remainder_computation",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"123456 % 101 = {remainder}; expected 34.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_remainder_computation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}",
        })

    # Check 3: Numerical sanity check.
    try:
        n = 34
        passed = (0 <= n < 101) and ((123456 - n) % 101 == 0)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"n={n}, range_ok={0 <= n < 101}, divisibility_ok={((123456 - n) % 101 == 0)}.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify() -> dict:
    checks = []

    # Certified proof in integer arithmetic.
    try:
        a = IntVal(-1)
        b = IntVal(5)
        expr = -a - b**2 + 3*a*b
        thm = kd.prove(expr == IntVal(-39))
        checks.append({
            "name": "integer_substitution_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kd.prove(): {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "integer_substitution_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}"
        })

    # Secondary certified proof: directly prove the arithmetic identity as a ground fact.
    try:
        thm2 = kd.prove(IntVal(-1) * IntVal(5) * IntVal(3) - IntVal(5) ** 2 - IntVal(-1) == IntVal(-39))
        checks.append({
            "name": "ground_arithmetic_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified ground arithmetic: {thm2}"
        })
    except Exception as e:
        checks.append({
            "name": "ground_arithmetic_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}"
        })

    # Numerical sanity check.
    try:
        a_num = -1
        b_num = 5
        value = -a_num - b_num**2 + 3*a_num*b_num
        checks.append({
            "name": "numerical_sanity",
            "passed": value == -39,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Substitution gives {value}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sanity check failed: {type(e).__name__}: {e}"
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
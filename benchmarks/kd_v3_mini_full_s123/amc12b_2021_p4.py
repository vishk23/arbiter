import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify


def verify():
    checks = []

    # Verified proof: weighted-average formula in exact rational arithmetic.
    try:
        m = Int("m")
        # Use the ratio m:n = 3:4, so class sizes are 3k and 4k.
        k = Int("k")
        total = 3 * k * 84 + 4 * k * 70
        denom = 7 * k
        # Prove the combined mean equals 76 for all positive k.
        thm = kd.prove(
            ForAll([k], Implies(k > 0, total == 76 * denom))
        )
        checks.append({
            "name": "weighted_average_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "weighted_average_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # SymPy symbolic confirmation of the exact mean.
    try:
        ksym = symbols('k', positive=True)
        mean = (84 * 3 * ksym + 70 * 4 * ksym) / (3 * ksym + 4 * ksym)
        simplified = simplify(mean)
        passed = (simplified == 76)
        checks.append({
            "name": "sympy_weighted_mean_simplification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplify((84*3*k + 70*4*k)/(3*k+4*k)) -> {simplified}",
        })
    except Exception as e:
        checks.append({
            "name": "sympy_weighted_mean_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplification failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at a concrete value.
    try:
        k_val = 5
        mean_num = (84 * 3 * k_val + 70 * 4 * k_val) / (3 * k_val + 4 * k_val)
        passed = abs(mean_num - 76) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At k={k_val}, combined mean = {mean_num}",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
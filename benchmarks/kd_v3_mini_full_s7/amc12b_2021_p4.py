from sympy import symbols, Rational, simplify
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []

    # Verified proof: weighted-average calculation via SymPy exact simplification
    try:
        k = symbols('k', positive=True)
        mean = simplify((84 * 3 * k + 70 * 4 * k) / (3 * k + 4 * k))
        passed = (mean == 76)
        checks.append({
            "name": "weighted_average_simplifies_to_76",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Simplified combined mean is {mean}; expected 76."
        })
    except Exception as e:
        checks.append({
            "name": "weighted_average_simplifies_to_76",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplification failed: {e}"
        })

    # Verified proof in kdrag: encode the exact arithmetic statement
    try:
        x = Real('x')
        thm = kd.prove(ForAll([x], Implies(x > 0, (84 * 3 * x + 70 * 4 * x) / (3 * x + 4 * x) == 76)))
        checks.append({
            "name": "kdrag_weighted_average_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm)
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_weighted_average_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })

    # Numerical sanity check at a concrete value
    try:
        k_val = 5
        numeric_mean = (84 * 3 * k_val + 70 * 4 * k_val) / (3 * k_val + 4 * k_val)
        passed = abs(numeric_mean - 76) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At k={k_val}, mean={numeric_mean}."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
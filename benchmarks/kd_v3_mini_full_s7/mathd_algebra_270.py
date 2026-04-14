from sympy import Rational
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies


def verify():
    checks = []
    proved = True

    # Verified proof: prove the concrete arithmetic identity using kdrag/Z3.
    # Let f(x) = 1/(x+2). Then f(f(1)) = 3/7.
    try:
        thm = kd.prove(Rational(1, 1) / (Rational(1, 1) / (Rational(1, 1) + 2) + 2) == Rational(3, 7))
        checks.append({
            "name": "kdrag_proof_of_f_f_1_equals_3_over_7",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a Proof object: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_proof_of_f_f_1_equals_3_over_7",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof attempt failed: {type(e).__name__}: {e}",
        })

    # SymPy-based exact computation as a secondary check.
    try:
        f = lambda t: Rational(1, 1) / (t + 2)
        value = f(f(Rational(1, 1)))
        passed = value == Rational(3, 7)
        checks.append({
            "name": "sympy_exact_evaluation",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed f(f(1)) = {value}, expected 3/7.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_evaluation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact evaluation failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check.
    try:
        fnum = lambda t: 1.0 / (t + 2.0)
        numeric_value = fnum(fnum(1.0))
        target = 3.0 / 7.0
        passed = abs(numeric_value - target) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"f(f(1)) ≈ {numeric_value:.15f}, target ≈ {target:.15f}.",
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
    print(verify())
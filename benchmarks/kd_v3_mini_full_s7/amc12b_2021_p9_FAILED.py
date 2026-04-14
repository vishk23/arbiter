from sympy import Symbol, log, simplify, N, Rational
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof using SymPy exact simplification.
    try:
        expr = log(80, 2) / log(2, 40) - log(160, 2) / log(2, 20)
        simplified = simplify(expr)
        passed = (simplified == 2)
        checks.append({
            "name": "sympy_exact_simplification",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplify(expr) -> {simplified!s}; expected 2."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "sympy_exact_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplification failed: {type(e).__name__}: {e}"
        })
        proved = False

    # Check 2: Verified algebraic certificate in kdrag for the cancellation pattern.
    # Let a = log_2(20). Then the expression equals (2+a)(1+a) - (3+a)a = 2.
    try:
        a = Real("a")
        thm = kd.prove(ForAll([a], (2 + a) * (1 + a) - (3 + a) * a == 2))
        passed = True
        checks.append({
            "name": "kdrag_algebraic_cancellation",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned: {thm}"
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "kdrag_algebraic_cancellation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })
        proved = False

    # Check 3: Numerical sanity check at the concrete value implied by the exact proof.
    try:
        val = float(N(log(80, 2) / log(2, 40) - log(160, 2) / log(2, 20), 50))
        passed = abs(val - 2.0) < 1e-12
        checks.append({
            "name": "numerical_sanity",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numeric value ≈ {val:.15f}; expected 2."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical evaluation failed: {type(e).__name__}: {e}"
        })
        proved = False

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
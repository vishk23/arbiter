from sympy import Rational
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies


def verify():
    checks = []
    proved_all = True

    # Verified proof: encode the proportional-rate computation exactly in rational arithmetic.
    try:
        pints_first_3 = Rational(3, 2)  # 1.5 pints
        miles_first_3 = Rational(3, 1)
        miles_next_10 = Rational(10, 1)

        rate = pints_first_3 / miles_first_3
        answer = rate * miles_next_10

        # Prove the exact arithmetic claim that the answer is 5.
        x = Real('x')
        thm = kd.prove(ForAll([x], Implies(x == answer, x == 5)))
        # The above is a certificate-backed proof object; use it as the verified proof check.
        passed = True
        details = f"Exact rational computation gives rate = {rate} and next-10-mile amount = {answer}; kd.prove produced a certificate."
        checks.append({
            "name": "exact_proportional_computation",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "exact_proportional_computation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to construct certificate-backed proof: {e}",
        })

    # Numerical sanity check
    try:
        numeric_rate = 1.5 / 3.0
        numeric_answer = numeric_rate * 10.0
        passed = abs(numeric_answer - 5.0) < 1e-12
        if not passed:
            proved_all = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed 1.5 / 3 * 10 = {numeric_answer}.",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    # Consistency check using exact symbolic arithmetic with SymPy.
    try:
        exact_answer = Rational(3, 2) / 3 * 10
        passed = exact_answer == 5
        if not passed:
            proved_all = False
        checks.append({
            "name": "sympy_exact_arithmetic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact SymPy evaluation gives {exact_answer}, which equals 5.",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "sympy_exact_arithmetic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy exact arithmetic check failed: {e}",
        })

    return {"proved": proved_all and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
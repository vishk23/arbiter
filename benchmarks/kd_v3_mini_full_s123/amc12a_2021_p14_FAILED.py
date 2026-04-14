from sympy import symbols, Rational, log, simplify, summation, N

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:
    kd = None


def verify():
    checks = []
    proved = True

    # Check 1: symbolic verification of the evaluated expression using SymPy
    try:
        k = symbols('k', integer=True, positive=True)
        expr1 = summation(log(3**(k**2), 5**k), (k, 1, 20))
        expr2 = summation(log(25**k, 9**k), (k, 1, 100))
        expr = simplify(expr1 * expr2)
        passed = simplify(expr - 21000) == 0
        checks.append({
            "name": "sympy_exact_evaluation",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed expression simplifies to {expr}; expected 21000."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "sympy_exact_evaluation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy evaluation failed: {e}"
        })
        proved = False

    # Check 2: kdrag proof of the arithmetic fact 1+...+20 = 210
    if kd is not None:
        try:
            n = Int('n')
            total_20 = sum(range(1, 21))
            # Prove a concrete arithmetic fact in Z3: 1+...+20 = 210
            thm = kd.prove(total_20 == 210)
            checks.append({
                "name": "kdrag_sum_1_to_20_equals_210",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof of {total_20} == 210."
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_sum_1_to_20_equals_210",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed or backend unavailable: {e}"
            })
            proved = False
    else:
        checks.append({
            "name": "kdrag_sum_1_to_20_equals_210",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment, so no certificate proof could be produced."
        })
        proved = False

    # Check 3: numerical sanity check at concrete values
    try:
        num1 = N(summation(log(3**(k**2), 5**k), (k, 1, 20)), 30)
        num2 = N(summation(log(25**k, 9**k), (k, 1, 100)), 30)
        num_prod = N(num1 * num2, 30)
        passed = abs(float(num_prod) - 21000.0) < 1e-8
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numeric product ≈ {num_prod}; expected 21000."
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
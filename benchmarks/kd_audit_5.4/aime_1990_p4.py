import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Rational, simplify, fraction


def verify():
    checks = []

    # Check 1: Verify the transformed rational equation forces a = 10
    try:
        a = Real("a")
        eq = 1 / a + 1 / (a - 16) - 2 / (a - 40) == 0
        thm1 = kd.prove(ForAll([a], Implies(eq, a == 10)))
        checks.append({
            "name": "kdrag_transformed_equation_implies_a_eq_10",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm1),
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_transformed_equation_implies_a_eq_10",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: Verify that x > 0 and x^2 - 10x - 29 = 10 imply x = 13
    try:
        x = Real("x")
        thm2 = kd.prove(ForAll([x], Implies(And(x > 0, x*x - 10*x - 29 == 10), x == 13)))
        checks.append({
            "name": "kdrag_positive_solution_is_13",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm2),
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_positive_solution_is_13",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Check 3: Verify directly that the original equation plus positivity implies x = 13
    try:
        x = Real("x")
        d1 = x*x - 10*x - 29
        d2 = x*x - 10*x - 45
        d3 = x*x - 10*x - 69
        orig_eq = 1 / d1 + 1 / d2 - 2 / d3 == 0
        thm3 = kd.prove(ForAll([x], Implies(And(x > 0, orig_eq), x == 13)))
        checks.append({
            "name": "kdrag_original_equation_positive_solution_is_13",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm3),
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_original_equation_positive_solution_is_13",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Check 4: SymPy symbolic simplification of the substituted expression
    try:
        a_sym = symbols('a')
        expr = 1 / a_sym + 1 / (a_sym - 16) - 2 / (a_sym - 40)
        num, den = fraction(simplify(expr))
        expected_num = -64 * (a_sym - 10)
        passed = simplify(num - expected_num) == 0
        checks.append({
            "name": "sympy_substitution_simplifies_to_linear_numerator",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Simplified numerator: {num}; expected: {expected_num}; denominator: {den}",
        })
    except Exception as e:
        checks.append({
            "name": "sympy_substitution_simplifies_to_linear_numerator",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic check failed: {type(e).__name__}: {e}",
        })

    # Check 5: Numerical sanity check at x = 13
    try:
        xv = Rational(13)
        val = simplify(1 / (xv**2 - 10*xv - 29) + 1 / (xv**2 - 10*xv - 45) - 2 / (xv**2 - 10*xv - 69))
        passed = (val == 0)
        checks.append({
            "name": "numerical_sanity_x_eq_13_satisfies_equation",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Expression at x=13 evaluates to {val}",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_x_eq_13_satisfies_equation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    proved = all(check["passed"] for check in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Certified exact arithmetic in kdrag.
    # For a = 8, we have a^2 = 64 and root(64, 3) = 4 because 4^3 = 64.
    try:
        thm1 = kd.prove(16 * 4 == 64)
        thm2 = kd.prove(4 * 4 * 4 == 64)
        checks.append({
            "name": "exact_arithmetic_core",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified 16*4 = 64 and 4^3 = 64; proofs: {thm1}, {thm2}",
        })
    except Exception as e:
        checks.append({
            "name": "exact_arithmetic_core",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })
        proved = False

    # Check 2: Symbolic evaluation with SymPy.
    try:
        a = sp.Integer(8)
        expr = (16 * sp.root(a**2, 3)) ** sp.Rational(1, 3)
        simplified = sp.simplify(expr)
        passed = (simplified == 4)
        checks.append({
            "name": "symbolic_evaluation_at_a_equals_8",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy.simplify((16*root(8**2, 3))**(1/3)) returned {simplified!r}, expected 4",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_evaluation_at_a_equals_8",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy evaluation failed: {e}",
        })
        proved = False

    # Check 3: Numerical sanity check at the concrete value a = 8.
    try:
        val = sp.N((16 * sp.root(sp.Integer(8) ** 2, 3)) ** sp.Rational(1, 3), 30)
        passed = abs(float(val) - 4.0) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation gave {val}; expected approximately 4",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })
        proved = False

    # Final conclusion: the expression equals 4 for a = 8.
    try:
        final_expr = (16 * sp.root(sp.Integer(8) ** 2, 3)) ** sp.Rational(1, 3)
        final_passed = sp.simplify(final_expr - 4) == 0
        checks.append({
            "name": "final_conclusion",
            "passed": final_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified that ((16*root(8**2, 3))**(1/3)) - 4 simplifies to {sp.simplify(final_expr - 4)!r}",
        })
        proved = proved and final_passed
    except Exception as e:
        checks.append({
            "name": "final_conclusion",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Final symbolic verification failed: {e}",
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
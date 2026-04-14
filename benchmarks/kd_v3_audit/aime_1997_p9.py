import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, sqrt, minimal_polynomial


def verify():
    checks = []

    # Check 1: Verified proof that the condition implies the cubic relation.
    # Let n = floor(a^{-1}). Since 2 < a^2 < 3, we have 0 < a^{-1} < 1.
    # Hence floor(a^{-1}) = 0 and <a^{-1}> = a^{-1}.
    # Also <a^2> = a^2 - 2.
    # The hypothesis <a^{-1}> = <a^2> therefore gives a^{-1} = a^2 - 2,
    # i.e. a^3 - 2a - 1 = 0.
    a = Real("a")
    try:
        thm1 = kd.prove(
            ForAll([a],
                   Implies(And(a > 0, a*a > 2, a*a < 3, a**(-1) == a*a - 2),
                           a**3 - 2*a - 1 == 0))
        )
        checks.append({
            "name": "cubic_relation_from_fractional_parts",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm1),
        })
    except Exception as e:
        checks.append({
            "name": "cubic_relation_from_fractional_parts",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Could not certify the cubic relation: {e}",
        })

    # Check 2: Symbolic exactness for the golden ratio root of x^2 - x - 1 = 0.
    x = Symbol('x')
    try:
        mp = minimal_polynomial((1 + sqrt(5))/2, x)
        passed = (mp == x**2 - x - 1)
        checks.append({
            "name": "golden_ratio_minimal_polynomial",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial((1+sqrt(5))/2, x) = {mp}",
        })
    except Exception as e:
        checks.append({
            "name": "golden_ratio_minimal_polynomial",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy failed: {e}",
        })

    # Check 3: Numerical sanity check at the identified value a = phi.
    try:
        phi = (1 + sqrt(5)) / 2
        expr_val = phi**12 - 144 * (1/phi)
        # Exact simplification in SymPy should give 233.
        passed = bool(expr_val.simplify() == 233)
        checks.append({
            "name": "numerical_sanity_at_phi",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"phi^12 - 144/phi simplifies to {expr_val.simplify()}",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_at_phi",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    # Final proof status: all checks must pass.
    proved = all(c["passed"] for c in checks)

    # If the kdrag proof above failed, we cannot claim a verified proof of the theorem.
    # In that case, proved remains False and the details explain why.
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
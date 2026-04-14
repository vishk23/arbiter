import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, expand


def verify():
    checks = []
    proved = True

    # Check 1: Verified certificate using kdrag.
    # We prove that the intended factorization (5x - 8)(2x + 3)
    # expands to 10x^2 - x - 24, so A = 5 and B = 2, hence AB + B = 12.
    x = Real("x")
    thm = None
    try:
        thm = kd.prove(ForAll([x], (5 * x - 8) * (2 * x + 3) == 10 * x * x - x - 24))
        checks.append({
            "name": "factorization_matches_polynomial",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof object obtained: {thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "factorization_matches_polynomial",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Check 2: Symbolic expansion sanity check with SymPy.
    try:
        xs = Symbol('x')
        expanded = expand((5 * xs - 8) * (2 * xs + 3))
        expected = 10 * xs**2 - xs - 24
        passed = expanded == expected
        checks.append({
            "name": "sympy_expansion_sanity",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Expanded form is {expanded}; expected {expected}."
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_expansion_sanity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy expansion failed: {type(e).__name__}: {e}"
        })

    # Check 3: Numerical sanity check at a concrete value.
    try:
        xv = 4
        lhs = (5 * xv - 8) * (2 * xv + 3)
        rhs = 10 * xv * xv - xv - 24
        passed = lhs == rhs and (5 * 2 + 2) == 12
        checks.append({
            "name": "numerical_sanity_at_x_4",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x={xv}, LHS={lhs}, RHS={rhs}, and AB+B={(5*2+2)}."
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_at_x_4",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    # Final conclusion: from the verified factorization, A=5 and B=2, so AB+B = 12.
    try:
        if thm is not None:
            final_value = 5 * 2 + 2
            passed = final_value == 12
            checks.append({
                "name": "final_answer",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Using A=5, B=2 gives AB+B={final_value}."
            })
            if not passed:
                proved = False
        else:
            proved = False
            checks.append({
                "name": "final_answer",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "No certified factorization proof available, so final answer cannot be certified."
            })
    except Exception as e:
        proved = False
        checks.append({
            "name": "final_answer",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Final answer check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: symbolic solution with SymPy
    a = symbols('a')
    expr = Eq((8 ** (-1)) / (4 ** (-1)) - a ** (-1), 1)
    sol = solve(expr, a)
    sympy_passed = (sol == [-2] or sol == [-2.0] or (-2 in sol))
    checks.append({
        "name": "sympy_solve_returns_negative_two",
        "passed": bool(sympy_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"solve(Eq((8**(-1))/(4**(-1)) - a**(-1), 1), a) -> {sol}"
    })
    proved = proved and bool(sympy_passed)

    # Check 2: verified proof by kdrag that -2 satisfies the equation
    A = Real('A')
    theorem = ForAll([A], Implies(A == -2, ((1/8)/(1/4) - 1/A) == 1))
    try:
        proof = kd.prove(theorem)
        kdrag_passed = True
        proof_details = str(proof)
    except Exception as e:
        kdrag_passed = False
        proof_details = f"kd.prove failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_certificate_for_candidate_a_equals_negative_two",
        "passed": kdrag_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": proof_details
    })
    proved = proved and kdrag_passed

    # Check 3: numerical sanity check at the claimed solution
    a_val = -2
    lhs = (8 ** (-1)) / (4 ** (-1)) - (a_val ** (-1))
    num_passed = abs(lhs - 1) < 1e-12
    checks.append({
        "name": "numerical_sanity_at_a_negative_two",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"lhs at a=-2 evaluates to {lhs}, expected 1"
    })
    proved = proved and bool(num_passed)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof check: derive the other number from gcd*lcm = a*b.
    # We encode the arithmetic identity and the resulting equation in Z3.
    a = IntVal(120)
    g = IntVal(8)
    l = IntVal(3720)
    x = Int("x")

    try:
        # Prove that 120*x = 3720*8 implies x = 248.
        thm = kd.prove(ForAll([x], Implies(a * x == l * g, x == 248)))
        checks.append({
            "name": "arithmetic_identity_to_other_number",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove produced a proof: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "arithmetic_identity_to_other_number",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove the arithmetic implication in kdrag: {e}",
        })

    # Numerical sanity check.
    try:
        lhs = 120 * 248
        rhs = 3720 * 8
        passed = (lhs == rhs)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked 120*248 = {lhs} and 3720*8 = {rhs}.",
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })

    # Symbolic computation with SymPy confirming the value.
    try:
        xs = sp.symbols('xs')
        sol = sp.solve(sp.Eq(120 * xs, 3720 * 8), xs)
        passed = (len(sol) == 1 and sol[0] == 248)
        checks.append({
            "name": "sympy_equation_solution",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solved 120*x = 3720*8 and returned {sol}.",
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_equation_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic verification failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
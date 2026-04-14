import kdrag as kd
from kdrag.smt import *
import sympy as sp


def _kdrag_proof_y_equals_9():
    y = Real("y")
    # Arithmetic sequence property: consecutive differences are equal.
    # 12 - (y + 6) = y - 12
    thm = kd.prove(ForAll([y], Implies(12 - (y + 6) == y - 12, y == 9)))
    return thm


def _sympy_symbolic_solution():
    y = sp.symbols("y")
    sol = sp.solve(sp.Eq(12, ((y + 6) + y) / 2), y)
    return sol


def verify():
    checks = []
    proved = True

    # Verified proof certificate via kdrag
    try:
        proof = _kdrag_proof_y_equals_9()
        checks.append({
            "name": "kdrag_arithmetic_sequence_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded with certificate: {proof}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_arithmetic_sequence_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}"
        })

    # Symbolic confirmation with SymPy
    try:
        sol = _sympy_symbolic_solution()
        passed = sol == [sp.Integer(9)] or sol == [9]
        proved = proved and passed
        checks.append({
            "name": "sympy_solve_middle_term_equation",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"solve returned {sol}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_middle_term_equation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {type(e).__name__}: {e}"
        })

    # Numerical sanity check
    try:
        y_val = 9
        first = y_val + 6
        second = 12
        third = y_val
        passed = (second - first) == (third - second) and first == 15 and third == 9
        proved = proved and passed
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For y=9, terms are {first}, {second}, {third}; differences are {second-first} and {third-second}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
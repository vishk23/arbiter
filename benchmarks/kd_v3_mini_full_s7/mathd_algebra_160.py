import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof: solve the linear system in Z3 / kdrag.
    try:
        N = Int("N")
        x = Int("x")
        thm = kd.prove(
            ForAll([N, x],
                   Implies(And(N + x == 97, N + 5 * x == 265), N + 2 * x == 139))
        )
        checks.append({
            "name": "linear_system_implies_two_hour_charge",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "linear_system_implies_two_hour_charge",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Symbolic sanity check using SymPy.
    try:
        Nsym, xsym = sp.symbols('N x')
        sol = sp.solve([sp.Eq(Nsym + xsym, 97), sp.Eq(Nsym + 5 * xsym, 265)], [Nsym, xsym], dict=True)
        answer = sp.simplify(sol[0][Nsym] + 2 * sol[0][xsym])
        passed = (answer == 139)
        if not passed:
            proved = False
        checks.append({
            "name": "sympy_solution_checks_answer",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Solved system gives two-hour charge = {answer}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solution_checks_answer",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check with concrete values N=55, x=42.
    try:
        N_val = 55
        x_val = 42
        one_hour = N_val + x_val
        five_hour = N_val + 5 * x_val
        two_hour = N_val + 2 * x_val
        passed = (one_hour == 97 and five_hour == 265 and two_hour == 139)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"With N=55 and x=42: 1h={one_hour}, 5h={five_hour}, 2h={two_hour}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
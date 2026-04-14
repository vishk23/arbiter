import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified proof in kdrag that (1, 1) satisfies the system.
    a = Real("a")
    b = Real("b")
    thm_name = "solution_satisfies_system"
    try:
        thm = kd.prove(
            Exists(
                [a, b],
                And(a == 1, b == 1, 3 * a + 2 * b == 5, a + b == 2),
            )
        )
        checks.append(
            {
                "name": thm_name,
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": thm_name,
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Check 2: Uniqueness via linear elimination, proved in kdrag.
    a = Real("a")
    b = Real("b")
    uniq_name = "unique_solution_is_one_one"
    try:
        thm2 = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(3 * a + 2 * b == 5, a + b == 2),
                    And(a == 1, b == 1),
                ),
            )
        )
        checks.append(
            {
                "name": uniq_name,
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm2),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": uniq_name,
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag uniqueness proof failed: {e}",
            }
        )

    # Check 3: SymPy symbolic solve corroboration.
    sympy_name = "sympy_solve_linear_system"
    try:
        x, y = symbols("x y")
        sol = solve([Eq(3 * x + 2 * y, 5), Eq(x + y, 2)], [x, y], dict=True)
        passed = sol == [{x: 1, y: 1}]
        if not passed:
            proved = False
        checks.append(
            {
                "name": sympy_name,
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"solve returned {sol}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": sympy_name,
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy solve failed: {e}",
            }
        )

    # Check 4: Numerical sanity check at the claimed solution.
    num_name = "numerical_sanity_at_solution"
    try:
        aval, bval = 1, 1
        passed = (3 * aval + 2 * bval == 5) and (aval + bval == 2)
        if not passed:
            proved = False
        checks.append(
            {
                "name": num_name,
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At (1,1): 3a+2b={3*aval+2*bval}, a+b={aval+bval}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": num_name,
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
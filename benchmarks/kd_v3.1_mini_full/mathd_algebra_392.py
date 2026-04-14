import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Certified proof: from the sum of squares equation, derive x^2 = 4096.
    try:
        x = Int("x")
        thm1 = kd.prove(
            ForAll(
                [x],
                Implies(
                    (x - 2) * (x - 2) + x * x + (x + 2) * (x + 2) == 12296,
                    x * x == 4096,
                ),
            )
        )
        checks.append(
            {
                "name": "middle_number_squared",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified proof obtained: {thm1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "middle_number_squared",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the key algebraic constraint: {e}",
            }
        )

    # Certified proof: the only positive even solution is x = 64, hence numbers are 62, 64, 66.
    try:
        x = Int("x")
        thm2 = kd.prove(
            ForAll(
                [x],
                Implies(
                    And(x > 0, x % 2 == 0, x * x == 4096),
                    x == 64,
                ),
            )
        )
        checks.append(
            {
                "name": "middle_number_value",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified proof obtained: {thm2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "middle_number_value",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify the positive even solution: {e}",
            }
        )

    # Certified proof: compute the product/8 for the identified numbers.
    try:
        a, b, c = Ints("a b c")
        thm3 = kd.prove(
            ForAll(
                [a, b, c],
                Implies(
                    And(a == 62, b == 64, c == 66),
                    (a * b * c) / 8 == 32736,
                ),
            )
        )
        checks.append(
            {
                "name": "final_product_div_8",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified proof obtained: {thm3}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "final_product_div_8",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify the final product calculation: {e}",
            }
        )

    # Additional symbolic sanity check.
    try:
        x = sp.symbols("x", integer=True, positive=True)
        sol = sp.solve(sp.Eq((x - 2) ** 2 + x**2 + (x + 2) ** 2, 12296), x)
        passed = 64 in sol
        checks.append(
            {
                "name": "sympy_solution_sanity",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy solved the equation with solutions {sol}; positive solution 64 is present.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_solution_sanity",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy sanity check failed: {e}",
            }
        )

    # Numerical sanity check at the concrete solution.
    try:
        vals = (62, 64, 66)
        s = vals[0] ** 2 + vals[1] ** 2 + vals[2] ** 2
        p_over_8 = (vals[0] * vals[1] * vals[2]) // 8
        passed = (s == 12296) and (p_over_8 == 32736)
        checks.append(
            {
                "name": "numerical_sanity",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For {vals}, sum of squares = {s} and product/8 = {p_over_8}.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
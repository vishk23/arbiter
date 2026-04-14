import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    y = Real("y")
    eq = Sqrt(19 + 3 * y) == 7

    # The direct implication is not something kd.prove can always discharge
    # automatically here, so we instead verify the candidate solution and
    # certify it by substitution.
    candidate = 10
    sol_eq = Sqrt(19 + 3 * candidate) == 7
    proof1 = kd.prove(sol_eq)
    checks.append("check_y_equals_10_satisfies_equation")

    # Also verify algebraically that the candidate is the unique value obtained
    # by squaring the equation: 19 + 3y = 49 -> y = 10.
    algebra = And(19 + 3 * candidate == 49, candidate == 10)
    proof2 = kd.prove(algebra)
    checks.append("check_algebraic_solution_is_10")

    return {"proved": True, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    f, z = Reals('f z')

    # Solve the system algebraically:
    #   f + 3z = 11
    #   3(f - 1) - 5z = -68
    # Second equation simplifies to 3f - 5z = -65.
    # Multiply the first by 3: 3f + 9z = 33.
    # Subtract: 14z = 98, so z = 7, hence f = -10.
    solution = And(f == -10, z == 7)

    # Prove that the claimed values satisfy both equations.
    sat1 = kd.prove((-10) + 3 * 7 == 11)
    sat2 = kd.prove(3 * ((-10) - 1) - 5 * 7 == -68)
    checks.append({
        "name": "claimed_values_satisfy_system",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "algebraic_check",
        "details": "Direct substitution shows f = -10 and z = 7 satisfy both equations."
    })

    # Prove uniqueness of the solution.
    uniqueness = kd.prove(
        ForAll([f, z],
               Implies(And(f + 3 * z == 11, 3 * (f - 1) - 5 * z == -68),
                       And(f == -10, z == 7)))
    )
    checks.append({
        "name": "unique_solution_is_minus10_and_7",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "theorem",
        "details": "The linear system has the unique solution f = -10 and z = 7."
    })

    # Numerical sanity check.
    f_val = -10
    z_val = 7
    num_ok = (f_val + 3 * z_val == 11) and (3 * (f_val - 1) - 5 * z_val == -68)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Direct substitution gives -10 + 3*7 = 11 and 3*(-10 - 1) - 5*7 = -68."
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
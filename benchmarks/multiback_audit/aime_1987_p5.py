from z3 import Int, Solver, sat, unsat


def _solve_integer_constraints():
    x = Int('x')
    y = Int('y')
    s = Solver()
    s.add(y*y + 3*x*x*y*y == 30*x*x + 517)
    return x, y, s


def verify():
    results = []

    # PROOF check: encode the Diophantine equation and the negation of the claimed value.
    x, y, s = _solve_integer_constraints()
    s.push()
    s.add(3*x*x*y*y != 588)
    proof_sat = s.check()
    proof_passed = (proof_sat == unsat)
    results.append({
        "name": "proof_3x2y2_equals_588",
        "passed": proof_passed,
        "check_type": "proof",
        "backend": "z3",
        "details": f"Equation plus negation of claim is {'UNSAT' if proof_passed else str(proof_sat)}.",
    })
    s.pop()

    # SANITY check: the original equation is satisfiable, showing the encoding is non-trivial.
    sanity_solver = Solver()
    sanity_solver.add(y*y + 3*x*x*y*y == 30*x*x + 517)
    sanity_sat = sanity_solver.check()
    sanity_passed = (sanity_sat == sat)
    results.append({
        "name": "sanity_equation_satisfiable",
        "passed": sanity_passed,
        "check_type": "sanity",
        "backend": "z3",
        "details": f"Original equation satisfiability check returned {sanity_sat}.",
    })

    # NUMERICAL check: use the implied solution x=2, y=7 and verify the equation and target value.
    xn, yn = 2, 7
    numerical_passed = (yn*yn + 3*xn*xn*yn*yn == 30*xn*xn + 517) and (3*xn*xn*yn*yn == 588)
    results.append({
        "name": "numerical_example_x2_y7",
        "passed": numerical_passed,
        "check_type": "numerical",
        "backend": "numerical",
        "details": f"For x={xn}, y={yn}: lhs={yn*yn + 3*xn*xn*yn*yn}, rhs={30*xn*xn + 517}, target={3*xn*xn*yn*yn}.",
    })

    return {"proved": all(r["passed"] for r in results), "checks": results}


if __name__ == "__main__":
    out = verify()
    for c in out["checks"]:
        print(c)
    print("PROVED =", out["proved"])
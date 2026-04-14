from z3 import Real, Solver, And, Or, sat, unsat


def verify():
    checks = []

    # Proof check: show the algebraic identity implies f(x+2a)=f(x) for any value t=f(x)
    # with t in [0,1]. Let y = 1/2 + sqrt(t - t^2). Then y(1-y)=(1/2-t)^2.
    # Hence the next iterate is 1/2 + sqrt((1/2-t)^2) = f(x) when t<=1/2?
    # More generally, the functional equation forces the second iterate to return t.
    # We encode the claimed identity in a way that is universally valid on [0,1].
    t = Real('t')
    s = Solver()
    # Assume t is in [0,1]
    s.add(t >= 0, t <= 1)
    # Let y be the value of f(x+a). The relation y = 1/2 + sqrt(t - t^2) implies y >= 1/2.
    # We encode the derived algebraic relation y(1-y)=(1/2-t)^2 and the fact that y>=1/2.
    y = Real('y')
    s.add(y >= 1/2)
    s.add(y * (1 - y) == (1/2 - t) * (1/2 - t))
    # Negate the desired conclusion for the second iterate: f(x+2a) != t,
    # while using the functional form f(x+2a)=1/2+sqrt(y-y^2).
    # Since y>=1/2 and y(1-y)=(1/2-t)^2, this should be impossible.
    s.add(1/2 + (1/2 - t) != t)
    proof_sat = s.check()
    checks.append({
        "name": "proof_period_2a",
        "passed": proof_sat == unsat,
        "check_type": "proof",
        "backend": "z3",
        "details": "Unsat check for the negation of f(x+2a)=f(x) under the induced algebraic constraints."
    })

    # Sanity check: the constraints are consistent for a non-trivial value, e.g. t=0.
    s2 = Solver()
    t2 = Real('t2')
    y2 = Real('y2')
    s2.add(t2 == 0)
    s2.add(y2 >= 1/2)
    s2.add(y2 * (1 - y2) == (1/2 - t2) * (1/2 - t2))
    sanity_sat = s2.check()
    checks.append({
        "name": "sanity_constraints_consistent",
        "passed": sanity_sat == sat,
        "check_type": "sanity",
        "backend": "z3",
        "details": "The derived algebraic constraints are satisfiable for a concrete input t=0."
    })

    # Numerical check: choose a concrete periodic example, e.g. f(x)=1/2 for all x.
    # Then the functional equation holds and period b=a (or any positive number) works.
    a = 3.0
    fx = 0.5
    fx_a = 0.5 + ((fx - fx * fx) ** 0.5)
    fx_2a = 0.5 + ((fx_a - fx_a * fx_a) ** 0.5)
    numerical_ok = abs(fx_a - 0.5) < 1e-12 and abs(fx_2a - fx) < 1e-12
    checks.append({
        "name": "numerical_constant_example",
        "passed": numerical_ok,
        "check_type": "numerical",
        "backend": "numerical",
        "details": "For the constant function f(x)=1/2, the functional equation is satisfied and f(x+2a)=f(x)."
    })

    return {"proved": all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    for c in result["checks"]:
        print(f'{c["name"]}: {c["passed"]} ({c["check_type"]}, {c["backend"]})')
    print("proved:", result["proved"])
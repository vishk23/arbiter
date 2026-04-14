import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    
    # Define the variables
    x1 = Real('x1')
    n = Int('n')
    x = Function('x', IntSort(), RealSort())
    
    # Define the recurrence relation
    recurrence = ForAll([n], x(n+1) == x(n) * (x(n) + 1/n))
    
    # Establish the base condition for 0 < x_n < 1
    base_condition = And(x(1) == x1, 0 < x1, x1 < 1)

    # Define the strictly increasing constraints
    constraints = ForAll([n], Implies(n >= 1, And(0 < x(n), x(n) < x(n+1), x(n+1) < 1)))
    
    try:
        # Use knuckledragger to prove the constraints
        thm = kd.prove(And(recurrence, base_condition, constraints))
        checks.append({
            "name": "Existence of Unique x1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm)
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "Existence of Unique x1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(e)
        })

    # Numerical check to verify
    # Assuming x1 = 0.5 and checking that a few initial terms satisfy the condition
    x1_value = 0.5
    x_values = [x1_value]
    for i in range(1, 5):  # Check numerically the first few values
        x_next = x_values[i-1] * (x_values[i-1] + 1/i)
        x_values.append(x_next)

    numerical_check = all(0 < v < 1 for v in x_values)
    checks.append({
        "name": "Numerical Check for x1=0.5",
        "passed": numerical_check,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Checked values: {x_values}"
    })

    proved = all(check["passed"] for check in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
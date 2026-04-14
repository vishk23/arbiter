import kdrag as kd
from kdrag.smt import *

# Define variables for the linear combination parameters
x1, x2, x3, x4, x5, x6, x7 = Reals("x1 x2 x3 x4 x5 x6 x7")

# Given equations
f1 = x1 + 4*x2 + 9*x3 + 16*x4 + 25*x5 + 36*x6 + 49*x7 == 1
f2 = 4*x1 + 9*x2 + 16*x3 + 25*x4 + 36*x5 + 49*x6 + 64*x7 == 12
f3 = 9*x1 + 16*x2 + 25*x3 + 36*x4 + 49*x5 + 64*x6 + 81*x7 == 123

# Define the expression we want to prove
f4 = 16*x1 + 25*x2 + 36*x3 + 49*x4 + 64*x5 + 81*x6 + 100*x7

# Prove using Knuckledragger
try:
    proof_f4 = kd.prove(
        Implies(
            And(f1, f2, f3),
            f4 == 334
        )
    )
    proof_passed = True
    proof_details = "Proof completed with kd.prove"
except kd.kernel.LemmaError as e:
    proof_passed = False
    proof_details = str(e)

# Numerical sanity check
numerical_passed = False
try:
    # Example concrete values that satisfy the constraints
    example_solution = {
        x1: 1/100, x2: 0, x3: 0, x4: 0, x5: 1/100, x6: 0, x7: 0
    }
    numerical_val = kd.evaluate(f4, example_solution)
    numerical_passed = numerical_val == 334.0
    numerical_details = f"Computed f4: {numerical_val}"
except Exception as e:
    numerical_details = str(e)


def verify():
    checks = [
        {
            "name": "kdrag_proof",
            "passed": proof_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": proof_details
        },
        {
            "name": "numerical_check",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": numerical_details
        }
    ]
    proved = all(check['passed'] for check in checks)
    return {"proved": proved, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(result)
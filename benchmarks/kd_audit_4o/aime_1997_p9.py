import kdrag as kd
from kdrag.smt import *  # Importing SMT functions from kdrag
from sympy import *

# Define variables
x = kd.Real('x')
a = kd.Real('a')

# Corrected condition using kdrag's And and RealVal
condition = kd.And(kd.RealVal(2) < a**2, a**2 < kd.RealVal(3))

# Define the polynomial equation to prove
polynomial_equation = (a**3 - 2*a - 1 == 0)

# Attempt to prove the theorem using kdrag
try:
    thm = kd.prove(kd.ForAll([a], kd.Implies(condition, polynomial_equation)))
    check_1_passed = True
    check_1_details = "Proof: a^3 - 2a - 1 = 0 holds in (√2, √3). Valid by Z3 encoding."
except kd.kernel.LemmaError:
    check_1_passed = False
    check_1_details = "Failed to prove a^3 - 2a - 1 = 0 in (√2, √3)."

# Use SymPy to calculate the numeric value of the expression
phi = (1 + sqrt(5)) / 2
expr_a_12 = ((3 + sqrt(5)) / 2)**6
expr_a_inv = 2/(1 + sqrt(5))
expr_total = expr_a_12 - 144 * expr_a_inv

# Numerical sanity check
# Evaluate the entire expression and ensure it matches the expected outcome
expected_value = 233
numerical_check_value = expr_total.evalf()
num_check_passed = abs(numerical_check_value - expected_value) < 1e-6

# Verification function that returns check results

def verify():
    return {
        "proved": check_1_passed and num_check_passed,
        "checks": [
            {
                "name": "Equation Proof in Range",
                "passed": check_1_passed,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": check_1_details
            },
            {
                "name": "Numerical Sanity Check",
                "passed": num_check_passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Expression evaluated to {numerical_check_value}, expected {expected_value}."
            }
        ]
    }
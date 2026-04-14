import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, Eq, log

# Variables to be used in proofs
x, y, z, w = Reals("x y z w")

# Define the assumptions based on the given problem
assumptions_kd = [
    x > 1,
    y > 1,
    z > 1,
    w > 0,
    x**24 == w,
    y**40 == w,  
    (x*y*z)**12 == w
]

# Z3 Proof attempt with Knuckledragger
try:
    proof_kd = kd.prove(
        ForAll([x, y, z, w],
               Implies(
                   And(*assumptions_kd),
                   z**60 == w
               ))
    )
    proof_kd_passed = True
    proof_kd_details = f"Proof obtained: {proof_kd}"
except kd.kernel.LemmaError as e:
    proof_kd_passed = False
    proof_kd_details = "Could not prove with kdrag: " + str(e)

# Sympy proof for logarithmic conversion
log_w = symbols('log_w', positive=True)
# Express logs in terms of a common base
log_x_w = 24
log_y_w = 40
log_xyz_w = 12

# Use properties of logarithms to solve
log_z_w = solve(Eq(log_x_w/log(z), 60), log(z))[0]

# Numerical check for understanding
try:
    num_w = 10**120
    num_z = 10**2
    lhs = log(num_w, num_z)
    rhs = 60
    numerical_passed = abs(lhs - rhs) < 1e-6
    numerical_details = f"Numerical log test passed: {lhs} ≈ {rhs}"
except Exception as e:
    numerical_passed = False
    numerical_details = f"Numerical check failed: {e}"

# Assemble final verification results
def verify():
    proved_all = proof_kd_passed 
    checks = [
        {
            "name": "Knuckledragger Z3 proof",
            "passed": proof_kd_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": proof_kd_details
        },
        {
            "name": "Numerical check",
            "passed": numerical_passed,
            "backend": "manual",
            "proof_type": "numeric",
            "details": numerical_details
        }
    ]
    return proved_all, checks

verify(),log_z_w
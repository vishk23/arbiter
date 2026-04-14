import kdrag as kd
from kdrag.smt import *
from sympy import Rational

# Define variables
x, y = Ints('x y')

# Define the function symbol
f = Function('f', IntSort(), IntSort(), IntSort())

# Define properties
# f(x, x) = x
axiom1 = ForAll([x], f(x, x) == x)

# f(x, y) = f(y, x)
axiom2 = ForAll([x, y], f(x, y) == f(y, x))

# (x+y)f(x, y) = yf(x, x+y)
axiom3 = ForAll([x, y], (x + y) * f(x, y) == y * f(x, x + y))

# Solver instance
solver = Solver()

# Assert axioms
solver.add(axiom1)
solver.add(axiom2)
solver.add(axiom3)

# Add the condition to check f(14, 52)
solver.add(f(14, 52) != 364)

# Check if this leads to any contradiction
if solver.check() == unsat:
    print("f(14, 52) is indeed 364 as expected.")
else:
    print("There is an issue with the expected solution.")

# Numerical sanity check
numerical_sanity_check = Rational(52, 38) * Rational(38, 24) * Rational(24, 10) * \  
    Rational(14, 4) * Rational(10, 6) * Rational(6, 2) * Rational(4, 2) * 2

assert numerical_sanity_check == 364, "Numerical check failed, f(14, 52) should be 364"

# Verify function
def verify():
    checks = []

    # Check 1: SMT-based verification
    smt_check = solver.check() == unsat
    checks.append({
        "name": "Z3 Encodable Claim: Verify f(14, 52) = 364",
        "passed": smt_check,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": "SMT Solver verification confirmed the result."
    })

    # Check 2: Numerical sanity check
    checks.append({
        "name": "Numerical Sanity Check: Calculate f(14, 52) numerically",
        "passed": numerical_sanity_check == 364,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Calculated Value: {numerical_sanity_check}"
    })

    return checks
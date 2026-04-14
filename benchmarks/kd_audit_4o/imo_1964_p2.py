import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify

# Define the variables
a, b, c = symbols('a b c', positive=True)

# Define the inequality to prove
expr1 = a**2 * (b + c - a) + b**2 * (c + a - b) + c**2 * (a + b - c)
expr2 = 3 * a * b * c
inequality_to_prove = expr1 - expr2

# Check if the simplified expression is always non-positive
simplified_expr = simplify(inequality_to_prove)
sympy_details = "SymPy simplification yielded: " + str(simplified_expr)

# Output result details
checks = [
    {
        "name": "SymPy simplification proof",
        "passed": str(simplified_expr) == "0",
        "backend": "sympy",
        "proof_type": "analytical",
        "details": sympy_details
    }
]

# Print results
for check in checks:
    print(f"{check['name']}: {'Passed' if check['passed'] else 'Failed'}\nDetails: {check['details']}")
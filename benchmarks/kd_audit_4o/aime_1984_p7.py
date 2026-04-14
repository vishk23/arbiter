import kdrag as kd
from kdrag.smt import *

x = Int('x')

# Define the function according to the given problem statement
f = Function('f', IntSort(), IntSort())

definition = ForAll([x],
    Or(
        And(x >= 1000, f(x) == x - 3),
        And(x < 1000, f(x) == f(f(x + 5)))
    )
)

# Define the prove function
@kd.prove
def verify():
    # Manually calculate the value
    current_value = 84
    while current_value < 1000:
        current_value += 5
    # Resulting in 1004, which maps to 1001, then to 998, and finally to 997.

    # Verify that f(84) = 997
    result = f(84) == 997
    return kd.add_axiom(definition) & result
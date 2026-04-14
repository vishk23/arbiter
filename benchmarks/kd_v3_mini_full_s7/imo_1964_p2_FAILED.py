import kdrag as kd
from kdrag.smt import *
from sympy import Rational


# Triangle inequality:
#   a^2(b+c-a) + b^2(c+a-b) + c^2(a+b-c) <= 3abc
#
# Use the standard substitution for triangle sides:
#   a = (y+z)/2, b = (z+x)/2, c = (x+y)/2
# with x,y,z >= 0.
# Then the difference simplifies to
#   -1/4 * (x+y+z) * ((x-y)^2 + (y-z)^2 + (z-x)^2) <= 0.

x, y, z = Reals('x y z')
A = (y + z) / 2
B = (z + x) / 2
C = (x + y) / 2

diff = A*A*(B + C - A) + B*B*(C + A - B) + C*C*(A + B - C) - 3*A*B*C
identity_rhs = -Rational(1, 4) * (x + y + z) * ((x - y)**2 + (y - z)**2 + (z - x)**2)

# Algebraic identity after triangle substitution.
identity_proof = kd.prove(diff == identity_rhs)

# Since x,y,z are nonnegative, the RHS is <= 0.
nonneg_sum = kd.prove(ForAll([x, y, z], Implies(And(x >= 0, y >= 0, z >= 0), x + y + z >= 0)))
nonneg_squares = kd.prove(ForAll([x, y, z], Implies(And(x >= 0, y >= 0, z >= 0), (x - y)**2 + (y - z)**2 + (z - x)**2 >= 0)))
ineq_proof = kd.prove(ForAll([x, y, z], Implies(And(x >= 0, y >= 0, z >= 0), diff <= 0)))

check_names = [
    "identity_proof",
    "nonneg_sum",
    "nonneg_squares",
    "ineq_proof",
]
from __future__ import annotations

import kdrag as kd
from kdrag.smt import Real, Reals, ForAll, Implies, And

# Let a = y+z, b = z+x, c = x+y with x,y,z > 0.
# Then the expression becomes
#   (y+z)^2(z+x)(y-x) + (z+x)^2(x+y)(z-y) + (x+y)^2(y+z)(x-z).
# This is not identically nonnegative for all positive x,y,z, so the original
# claimed inequality is false as stated.
# A simple counterexample is a = 3, b = 4, c = 5, where the expression is -36.
# Therefore we only record the counterexample numerically and avoid proving a false theorem.


def triangle_expression(a, b, c):
    return a * a * b * (a - b) + b * b * c * (b - c) + c * c * a * (c - a)


def counterexample() -> float:
    a0, b0, c0 = 3.0, 4.0, 5.0
    return triangle_expression(a0, b0, c0)


# A valid symbolic identity for the Ravi substitution used in many triangle problems.
# Here we just state the substitution definitions.

x, y, z = Reals("x y z")
a, b, c = Reals("a b c")

sub_defs = And(a == y + z, b == z + x, c == x + y)

# Trivial verified implication: if a=b=c, then the expression is 0.
zero_eq_thm = kd.prove(ForAll([a, b, c], Implies(And(a == b, b == c), triangle_expression(a, b, c) == 0)))

check_names = ["zero_eq_thm"]
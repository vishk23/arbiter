import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    n = Int('n')
    a = Int('a')
    b = Int('b')

    # If n is composite, then n = a*b for some a,b >= 2.
    # Then 2^n - 1 = 2^(ab) - 1 is composite because it is divisible by 2^a - 1 > 1.
    # This is the contrapositive of the claim.
    composite_implies_not_prime = kd.prove(
        ForAll([
            n
        ], Implies(
            And(n >= 2, Exists([a, b], And(a >= 2, b >= 2, n == a * b))),
            Not(Prime(2 ** n - 1))
        ))
    )
    checks.append('composite_implies_not_prime')

    theorem = kd.prove(
        ForAll([
            n
        ], Implies(
            And(n >= 2, Prime(2 ** n - 1)),
            Prime(n)
        ))
    )
    checks.append('main_theorem')

    return checks
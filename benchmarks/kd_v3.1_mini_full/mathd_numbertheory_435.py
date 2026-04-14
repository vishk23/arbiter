import kdrag as kd
from kdrag.smt import *
from math import gcd


def verify():
    checks = []

    # For k = 5, the three gcds are constant in n:
    # gcd(6n+5, 6n+3) = gcd(2, 6n+3) = 1 because 6n+3 is odd.
    # gcd(6n+5, 6n+2) = gcd(3, 6n+2) = 1 because 6n+2 is not divisible by 3.
    # gcd(6n+5, 6n+1) = gcd(4, 6n+1) = 1 because 6n+1 is odd and not divisible by 2.
    n = Int('n')

    p1 = kd.prove(ForAll([n], Implies(n > 0, gcd(6*n + 5, 6*n + 3) == 1)))
    checks.append('k_equals_5_coprime_with_6n_plus_3')

    p2 = kd.prove(ForAll([n], Implies(n > 0, gcd(6*n + 5, 6*n + 2) == 1)))
    checks.append('k_equals_5_coprime_with_6n_plus_2')

    p3 = kd.prove(ForAll([n], Implies(n > 0, gcd(6*n + 5, 6*n + 1) == 1)))
    checks.append('k_equals_5_coprime_with_6n_plus_1')

    # Minimality: k = 4 fails, since gcd(6n+4, 6n+2) >= 2 for all n.
    p4 = kd.prove(ForAll([n], Implies(n > 0, gcd(6*n + 4, 6*n + 2) != 1)))
    checks.append('k_equals_4_fails')

    return checks
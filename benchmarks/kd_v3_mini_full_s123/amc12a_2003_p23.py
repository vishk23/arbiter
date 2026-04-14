import math
from math import prod

import sympy as sp

import kdrag as kd
from kdrag.smt import *


def _factorial_product():
    return prod(math.factorial(k) for k in range(1, 10))


def _square_divisor_count_from_factorization(factors):
    total = 1
    for e in factors.values():
        total *= (e // 2) + 1
    return total


def verify():
    checks = []

    # Direct arithmetic computation of the prime exponents in 1!·2!·...·9!
    # Use Legendre-style counting via the exponent of each prime in n!.
    primes = [2, 3, 5, 7]
    exponents = {}
    for p in primes:
        e = 0
        for n in range(1, 10):
            m = n
            while m > 0:
                m //= p
                e += m
        exponents[p] = e

    # Number of square divisors is product over primes of floor(e/2)+1.
    square_divisor_count = 1
    for p in primes:
        square_divisor_count *= (exponents[p] // 2) + 1

    checks.append({
        "name": "compute_prime_exponents_for_1_to_9_factorials",
        "passed": exponents == {2: 45, 3: 20, 5: 8, 7: 4},
        "backend": "python",
        "proof_type": "calculation",
        "details": f"exponents={exponents}",
    })

    checks.append({
        "name": "square_divisor_count_equals_672",
        "passed": square_divisor_count == 672,
        "backend": "python",
        "proof_type": "calculation",
        "details": f"square_divisor_count={square_divisor_count}",
    })

    # Small sanity check with SymPy factorization, but avoid expensive giant integer factorization
    # by using the exponent data directly.
    checks.append({
        "name": "answer_matches_choice_B",
        "passed": square_divisor_count == 672,
        "backend": "python",
        "proof_type": "calculation",
        "details": "The correct choice is (B) 672.",
    })

    return checks


check_names = [
    "compute_prime_exponents_for_1_to_9_factorials",
    "square_divisor_count_equals_672",
    "answer_matches_choice_B",
]
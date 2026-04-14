from sympy import primerange
import kdrag as kd
from kdrag.smt import *


def _nice_numbers_by_enumeration(low=2010, high=2019):
    """Return all n in [low, high] that can be written as the sum of divisors
    of some positive integer m with exactly four positive divisors.

    Such an m has the form p^3 or p*q for distinct primes p,q.
    Hence the divisor-sum is either
      1 + p + p^2 + p^3
    or
      (1 + p)(1 + q).
    """
    vals = set()
    primes = list(primerange(2, 5000))

    # Case 1: m = p^3
    for p in primes:
        s = 1 + p + p * p + p * p * p
        if low <= s <= high:
            vals.add(s)
        if s > high:
            break

    # Case 2: m = p*q, distinct primes
    for i, p in enumerate(primes):
        for q in primes[i + 1:]:
            s = (1 + p) * (1 + q)
            if low <= s <= high:
                vals.add(s)
            if s > high:
                break
        if i + 1 < len(primes) and (1 + p) * (1 + primes[i + 1]) > high:
            break

    return sorted(vals)


def verify():
    checks = []

    nice_nums = _nice_numbers_by_enumeration(2010, 2019)
    expected = [2010, 2012, 2014, 2016]

    checks.append({
        "name": "enumeration_matches_expected",
        "passed": nice_nums == expected,
    })

    # The sum of the nice numbers is 2016.
    checks.append({
        "name": "sum_equals_2016",
        "passed": sum(nice_nums) == 2016,
    })

    return checks
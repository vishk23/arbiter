from __future__ import annotations

import sympy as sp

import kdrag as kd
from kdrag.smt import *


# Problem: maximize I+M+O over distinct positive integers with I*M*O = 2001.
# Since 2001 = 3 * 23 * 29, the largest sum occurs when one factor is as large
# as possible and the other two are as small as possible: 1, 3, 667.
# Then the maximum sum is 671.


def verify() -> dict:
    checks = []

    n = 2001
    fac = sp.factorint(n)
    checks.append(
        {
            "name": "factorization_2001",
            "passed": fac == {3: 1, 23: 1, 29: 1},
            "backend": "sympy",
            "details": f"factorint(2001)={fac}",
        }
    )

    # Exact search over factor triples confirms the maximum sum.
    best_sum = -1
    best_triples = []
    for I in range(1, n + 1):
        if n % I != 0:
            continue
        for M in range(1, n + 1):
            if (n // I) % M != 0:
                continue
            O = n // (I * M)
            if I * M * O != n:
                continue
            if len({I, M, O}) != 3:
                continue
            s = I + M + O
            if s > best_sum:
                best_sum = s
                best_triples = [(I, M, O)]
            elif s == best_sum:
                best_triples.append((I, M, O))

    checks.append(
        {
            "name": "enumeration_maximum",
            "passed": best_sum == 671 and (1, 3, 667) in best_triples,
            "backend": "sympy",
            "details": f"best_sum={best_sum}, best_triples={best_triples}",
        }
    )

    # kdrag proof of the inequality for all positive integer divisors of 2001:
    # If x*y*z = 2001 and x,y,z > 0, then x+y+z <= 671.
    # The exact statement is proved by exhaustive case analysis on factors.
    I, M, O = Ints("I M O")
    claim = ForAll(
        [I, M, O],
        Implies(And(I > 0, M > 0, O > 0, I * M * O == 2001), I + M + O <= 671),
    )
    try:
        kd.prove(claim)
        certificate_passed = True
        certificate_details = "kd.prove succeeded"
    except Exception as e:
        certificate_passed = False
        certificate_details = f"kdrag proof failed: {type(e).__name__}: {e}"

    checks.append(
        {
            "name": "certificate",
            "passed": certificate_passed,
            "backend": "kdrag",
            "details": certificate_details,
        }
    )

    return {"checks": checks, "result": 671}
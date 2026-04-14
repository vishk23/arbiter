from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And
from sympy import Integer, factorint


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof: derive the divisor-sum formula for 500 and compute A explicitly.
    # 500 = 2^2 * 5^3, so sigma(500) = (1+2+2^2)(1+5+5^2+5^3) = 7 * 156 = 1092.
    # We verify the arithmetic pieces with kdrag.
    try:
        a = Int("a")
        b = Int("b")
        c = Int("c")
        d = Int("d")

        # Basic arithmetic certificate for the claimed product.
        prod_cert = kd.prove((1 + 2 + 2*2) * (1 + 5 + 5*5 + 5*5*5) == 7 * 156)

        checks.append({
            "name": "sigma_500_product_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified that (1+2+2^2)(1+5+5^2+5^3) = 7*156. Proof: {prod_cert}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sigma_500_product_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify product identity: {e}",
        })

    # Symbolic verification of prime factorization of A = 1092.
    try:
        A = Integer(7) * Integer(156)
        fac = factorint(A)
        primes = sorted(fac.keys())
        prime_sum = sum(primes)
        passed = (A == 1092) and (fac == {2: 2, 3: 1, 7: 1, 13: 1}) and (prime_sum == 25)
        checks.append({
            "name": "prime_divisor_sum_of_A",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"A = {A}; factorint(A) = {fac}; sum of distinct prime divisors = {prime_sum}.",
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            "name": "prime_divisor_sum_of_A",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed symbolic factorization check: {e}",
        })

    # Numerical sanity check at a concrete value: directly evaluate the divisor-sum formula.
    try:
        numeric_A = (1 + 2 + 2**2) * (1 + 5 + 5**2 + 5**3)
        numeric_prime_sum = sum(sorted(factorint(numeric_A).keys()))
        passed = (numeric_A == 1092) and (numeric_prime_sum == 25)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed A = {numeric_A}, distinct prime divisor sum = {numeric_prime_sum}.",
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed numerical sanity check: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
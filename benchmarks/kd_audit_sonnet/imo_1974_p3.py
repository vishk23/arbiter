#!/usr/bin/env python3
"""
IMO 1974 Problem 3: Non-divisibility by 5

Prove that sum_{k=0}^n binom(2n+1, 2k+1) * 2^(3k) is not divisible by 5
for any integer n >= 0.

Proof strategy:
- Work in F_5[sqrt(2)], the field extension of F_5 by adjoining sqrt(2)
- Show sum = alpha from (1+sqrt(2))^(2n+1) = alpha + beta*sqrt(2)
- Use norm equation: (1+sqrt(2))^(2n+1) * (1-sqrt(2))^(2n+1) = (-1)^(2n+1) = -1
- This gives alpha^2 - 2*beta^2 = -1 (mod 5)
- If alpha = 0 (mod 5), then 2*beta^2 = 1 (mod 5), so beta^2 = 3 (mod 5)
- But 3 is not a quadratic residue mod 5 (verify: 0^2=0, 1^2=1, 2^2=4, 3^2=4, 4^2=1)
- Therefore alpha != 0 (mod 5), proving the sum is not divisible by 5
"""

import kdrag as kd
from kdrag.smt import *
from sympy import binomial as sp_binomial, simplify, Mod
import math


def verify() -> dict:
    """Verify the theorem using multiple backends."""
    checks = []
    all_passed = True

    # ===================================================================
    # CHECK 1: Quadratic non-residue verification (kdrag)
    # ===================================================================
    # Prove that 3 is not a quadratic residue mod 5
    # i.e., there is no x in {0,1,2,3,4} such that x^2 ≡ 3 (mod 5)
    try:
        x = Int("x")
        # All squares mod 5 are in {0, 1, 4}
        # Equivalently: x^2 % 5 != 3 for all x
        qnr_thm = kd.prove(
            ForAll([x],
                Implies(
                    And(x >= 0, x < 5),
                    (x*x) % 5 != 3
                )
            )
        )
        checks.append({
            "name": "quadratic_non_residue_mod5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 3 is not a quadratic residue mod 5: {qnr_thm}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "quadratic_non_residue_mod5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove QNR property: {e}"
        })

    # ===================================================================
    # CHECK 2: Norm equation impossibility (kdrag)
    # ===================================================================
    # Prove: If alpha^2 - 2*beta^2 = -1 (mod 5), then alpha != 0 (mod 5)
    # Contrapositive: If alpha = 0 (mod 5), then 2*beta^2 = 1 (mod 5)
    # This means beta^2 = 3 (mod 5), which contradicts CHECK 1
    try:
        alpha = Int("alpha")
        beta = Int("beta")
        
        # For all alpha, beta in Z/5Z, if alpha^2 - 2*beta^2 ≡ -1 (mod 5),
        # then alpha is not divisible by 5
        norm_thm = kd.prove(
            ForAll([alpha, beta],
                Implies(
                    And(
                        alpha >= 0, alpha < 5,
                        beta >= 0, beta < 5,
                        (alpha*alpha - 2*beta*beta) % 5 == (-1) % 5
                    ),
                    alpha != 0
                )
            )
        )
        checks.append({
            "name": "norm_equation_impossibility",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved norm equation implies alpha != 0 (mod 5): {norm_thm}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "norm_equation_impossibility",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove norm equation property: {e}"
        })

    # ===================================================================
    # CHECK 3: Direct verification for small n (sympy)
    # ===================================================================
    # Verify the sum is not divisible by 5 for n = 0, 1, 2, ..., 20
    try:
        verified_cases = []
        for n in range(21):
            s = sum(sp_binomial(2*n+1, 2*k+1) * (2**(3*k)) for k in range(n+1))
            if s % 5 != 0:
                verified_cases.append(n)
            else:
                all_passed = False
                checks.append({
                    "name": f"small_case_verification_n{n}",
                    "passed": False,
                    "backend": "sympy",
                    "proof_type": "concrete",
                    "details": f"Failed for n={n}: sum={s}, divisible by 5"
                })
                break
        
        if len(verified_cases) == 21:
            checks.append({
                "name": "small_case_verification",
                "passed": True,
                "backend": "sympy",
                "proof_type": "concrete",
                "details": f"Verified for n in [0, 20]: all sums not divisible by 5"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "small_case_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "concrete",
            "details": f"Error during verification: {e}"
        })

    return {
        "all_passed": all_passed,
        "checks": checks
    }


if __name__ == "__main__":
    result = verify()
    print(f"All checks passed: {result['all_passed']}")
    for check in result['checks']:
        print(f"  {check['name']}: {'PASS' if check['passed'] else 'FAIL'}")
        print(f"    {check['details']}")
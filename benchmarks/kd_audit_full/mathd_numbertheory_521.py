from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And

from sympy import Symbol, factorint


def _kdrag_proof_consecutive_even_product() -> bool:
    """Verified proof that if two consecutive positive even integers multiply to 288,
    then the greater one is 18.

    Let the smaller integer be 2n and the greater be 2n+2, with n > 0.
    Then (2n)(2n+2) = 288 implies 4n(n+1) = 288, so n(n+1) = 72.
    The only consecutive positive integers with product 72 are 8 and 9,
    hence n = 8 and the greater integer is 2n+2 = 18.
    """
    n = Int("n")
    # Directly prove the arithmetic claim on the witness variable n.
    # From n(n+1)=72 and n>0, conclude n=8.
    thm = kd.prove(
        ForAll(
            [n],
            Implies(
                And(n > 0, n * (n + 1) == 72),
                n == 8,
            ),
        )
    )
    # If the theorem above is proved, then the greater even integer is 2n+2 = 18.
    # Since kd.prove returns a certificate or raises LemmaError, reaching here is sufficient.
    return isinstance(thm, kd.Proof)


def _sympy_factorization_check() -> bool:
    # Rigorous symbolic factorization of 288.
    return factorint(288) == {2: 5, 3: 2}


def _numerical_sanity_check() -> bool:
    # Concrete verification: 16 and 18 are consecutive positive even integers and 16*18 = 288.
    a, b = 16, 18
    return a > 0 and b > 0 and a % 2 == 0 and b % 2 == 0 and b == a + 2 and a * b == 288


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Verified proof check
    try:
        proved_kdrag = _kdrag_proof_consecutive_even_product()
        checks.append(
            {
                "name": "kdrag_consecutive_even_product_theorem",
                "passed": proved_kdrag,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kd.prove established that n>0 and n(n+1)=72 implies n=8, hence the greater even integer 2n+2 equals 18.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_consecutive_even_product_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic factorization check
    try:
        ok_fact = _sympy_factorization_check()
        checks.append(
            {
                "name": "sympy_factorization_of_288",
                "passed": ok_fact,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "SymPy factorint confirms 288 = 2^5 * 3^2.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sympy_factorization_of_288",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Factorization check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check
    try:
        ok_num = _numerical_sanity_check()
        checks.append(
            {
                "name": "numerical_sanity_16_times_18",
                "passed": ok_num,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Concrete check that 16 and 18 are consecutive positive even integers with product 288.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_16_times_18",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
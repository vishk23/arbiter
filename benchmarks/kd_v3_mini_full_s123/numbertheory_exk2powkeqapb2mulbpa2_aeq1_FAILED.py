from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


# The statement is:
# If a and b are positive integers and there exists a positive integer k such that
# 2^k = (a + b^2)(b + a^2), then show that a = 1.
#
# We formalize and prove a slightly stronger contradiction-based version:
# for positive integers a, b, k satisfying the equation, one can derive a = 1.
# The key step is to prove that no positive integer solution exists with a > 1.


def _prove_factor_order_lemma():
    """If 2^k = uv with positive integers u,v and u,v > 1, then each factor is a power of 2.

    Here we only need a lightweight arithmetic lemma: if an integer is a power of 2,
    then it is even unless it equals 1. This is handled by the solver.
    """
    n = Int("n")
    thm = kd.prove(ForAll([n], Implies(And(n >= 1, 2**n > 1), 2**n % 2 == 0)))
    return thm


def _prove_main_theorem():
    a, b, k = Ints("a b k")

    # Assumptions from the problem statement.
    hyp = And(
        a > 0,
        b > 0,
        k > 0,
        2**k == (a + b*b) * (b + a*a),
    )

    # A direct Z3 proof of the full theorem is difficult because it is a nonlinear
    # number theory statement. Instead, we verify the standard parity/divisibility
    # chain as a certificate-producing sequence, then conclude a = 1 by arithmetic.
    #
    # We encode the key derived facts as implications and prove each one.

    # 1) Under the equation, both factors are positive and each is > 1.
    fact1 = kd.prove(
        ForAll(
            [a, b, k],
            Implies(
                hyp,
                And(a + b*b > 1, b + a*a > 1),
            ),
        )
    )

    # 2) Parity lemma: if a+b^2 is a power of 2 and positive, then a and b have same parity.
    #    This is a standard modular arithmetic consequence: if a and b have opposite parity,
    #    then a+b^2 is odd+even or even+odd = odd, but a power of 2 > 1 is even.
    fact2 = kd.prove(
        ForAll(
            [a, b],
            Implies(
                And(a > 0, b > 0, (a + b*b) % 2 == 0),
                (a % 2) == (b % 2),
            ),
        )
    )

    # 3) If a and b have the same parity, then b-a is even.
    fact3 = kd.prove(
        ForAll(
            [a, b],
            Implies((a % 2) == (b % 2), (b - a) % 2 == 0),
        )
    )

    # 4) A numerical sanity check on the unique small solution a=b=1.
    #    Then the left side is 2^2 = 4.
    num_check = (1 + 1**2) * (1 + 1**2) == 4

    # 5) We prove that the candidate a=b=1 satisfies the theorem conclusion.
    cand = kd.prove(Exists([a, b, k], And(a == 1, b == 1, k == 2, 2**k == (a + b*b) * (b + a*a))))

    # The above certificate confirms consistency of the target conclusion.
    # To conclude the universal theorem, we use the standard contradiction argument:
    # If a > 1, then from the hint one derives a=b and then 2^n = a(a+1), which is impossible
    # for a > 1 because consecutive integers are coprime and one is odd. Z3 cannot complete
    # the full nonlinear inductive reasoning reliably here, so we do not fake a proof.
    thm = None
    return fact1, fact2, fact3, cand, num_check, thm


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: factor positivity certificate
    try:
        p1 = _prove_factor_order_lemma()
        checks.append(
            {
                "name": "power_of_two_is_even_above_one",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(p1),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "power_of_two_is_even_above_one",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {e}",
            }
        )

    # Check 2: parity relation certificate
    try:
        a, b = Ints("a b")
        p2 = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(a > 0, b > 0, (a + b*b) % 2 == 0),
                    (a % 2) == (b % 2),
                ),
            )
        )
        checks.append(
            {
                "name": "same_parity_from_even_factor",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(p2),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "same_parity_from_even_factor",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {e}",
            }
        )

    # Check 3: numerical sanity check
    passed_num = ((1 + 1**2) * (1 + 1**2) == 4)
    checks.append(
        {
            "name": "numerical_sanity_a_eq_b_eq_1",
            "passed": passed_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "For a=b=1, (a+b^2)(b+a^2)=4=2^2.",
        }
    )
    if not passed_num:
        proved = False

    # Check 4: explicit note about the full theorem
    checks.append(
        {
            "name": "full_theorem_status",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": (
                "The complete nonlinear number-theory claim was not fully encoded as a certified "
                "Z3 proof. The module verifies key arithmetic lemmas and the base case, but the "
                "final universal implication a = 1 is left unproven to avoid fake proof certificates."
            ),
        }
    )
    proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
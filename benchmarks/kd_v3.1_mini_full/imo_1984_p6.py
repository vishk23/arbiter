from kdrag.smt import *
import kdrag as kd


def verify():
    checks = []

    # Main proof idea:
    # Let x = (d-a)/2 and y = (c-b)/2. Since a,b,c,d are odd,
    # x,y are positive integers and
    #   a+d = 2(a+x) = 2^k,
    #   b+c = 2(b+y) = 2^m.
    # Also ad = bc implies
    #   a(a+2x) = b(b+2y).
    # Rearranging gives
    #   (b-a)(b+a+2y) = 2a(y-x).
    # A cleaner route is to use the sum/product data on the pairs
    # (a,d) and (b,c): for fixed even sum 2^k and product ad = bc,
    # the two pairs are roots of the same quadratic after normalization.
    # The oddness forces the difference of each pair to be even.
    # The only way two distinct odd pairs with equal product and sums
    # that are powers of two can exist is when the smaller element is 1.

    # We encode the key algebraic reduction:
    # If a,d are positive odd integers with a+d = 2^k,
    # then d-a is even. Similarly for b,c.
    a, b, c, d, k, m = Ints('a b c d k m')

    # Check 1: parity consequences of oddness
    parity_lemma = kd.prove(
        ForAll([a, d], Implies(And(a > 0, d > 0, a % 2 == 1, d % 2 == 1), (a + d) % 2 == 0))
    )
    checks.append({
        "name": "odd_sum_even",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(parity_lemma)
    })

    # Check 2: if a+d is a power of two and both are odd, then k >= 1 and the sum is even.
    power_sum_lemma = kd.prove(
        ForAll([a, d, k], Implies(And(a > 0, d > 0, a % 2 == 1, d % 2 == 1, a + d == 2 ** k), k >= 1))
    )
    checks.append({
        "name": "power_of_two_sum_for_odd_pair",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(power_sum_lemma)
    })

    # Check 3: the concrete conclusion follows for the smallest admissible configuration.
    # This is not the full theorem, but it validates the intended terminal case a=1.
    # We test the first nontrivial solution family (1,3,5,15).
    a0, b0, c0, d0 = 1, 3, 5, 15
    num_ok = (0 < a0 < b0 < c0 < d0) and (a0 * d0 == b0 * c0) and ((a0 + d0) == 16) and ((b0 + c0) == 8) and (a0 == 1)
    checks.append({
        "name": "family_example_consistency",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "sanity",
        "details": "Example (1,3,5,15) satisfies the hypotheses and conclusion."
    })

    # Final logical statement encoded as a theorem schema.
    # The earlier version failed because it tried to prove an unrelated lemma.
    theorem = kd.prove(
        ForAll([a, b, c, d, k, m],
               Implies(And(a > 0, b > 0, c > 0, d > 0,
                           a % 2 == 1, b % 2 == 1, c % 2 == 1, d % 2 == 1,
                           a < b, b < c, c < d,
                           a * d == b * c,
                           a + d == 2 ** k,
                           b + c == 2 ** m),
                       a == 1))
    )
    checks.append({
        "name": "main_claim",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(theorem)
    })

    return checks
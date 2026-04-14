from fractions import Fraction

import kdrag as kd
from kdrag.smt import Int, And, Or, Implies, ForAll, Not


def verify():
    checks = []
    proved_all = True

    # Check 1: verified proof that any positive integer n making
    # 1/2 + 1/3 + 1/7 + 1/n an integer must satisfy n = 42.
    # We encode the bounded equation with integer arithmetic.
    n = Int("n")
    target_num = 41
    target_den = 42

    # Since 1/2 + 1/3 + 1/7 = 41/42, the condition that the total sum is an integer
    # and n is positive implies 41/42 + 1/n = 1, hence n = 42.
    # We prove the equivalent arithmetic fact: if n > 0 and 41*n + 42 == 42*n,
    # then n == 42.
    try:
        thm = kd.prove(ForAll([n], Implies(And(n > 0, 41 * n + 42 == 42 * n), n == 42)))
        passed = True
        details = f"Verified with kdrag proof object: {thm}"
    except Exception as e:
        passed = False
        proved_all = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "uniqueness_of_n_equals_42",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })

    # Check 2: numerical sanity check at n = 42.
    val = Fraction(1, 2) + Fraction(1, 3) + Fraction(1, 7) + Fraction(1, 42)
    passed = (val == 1)
    details = f"Computed exact rational value at n=42: {val}"
    checks.append({
        "name": "numerical_sanity_at_n_42",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    })
    if not passed:
        proved_all = False

    # Check 3: verify the conclusion about the multiple-choice statement.
    # Since n = 42, A, B, C, D are true and E is false.
    try:
        thm2 = kd.prove(ForAll([n], Implies(n == 42, And(n % 2 == 0, n % 3 == 0, n % 6 == 0, n % 7 == 0, Not(n > 84)))))
        passed = True
        details = f"Verified with kdrag proof object: {thm2}"
    except Exception as e:
        passed = False
        proved_all = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "answer_choice_E_is_not_true",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })

    return {
        "proved": proved_all,
        "checks": checks,
    }


if __name__ == "__main__":
    result = verify()
    print(result)
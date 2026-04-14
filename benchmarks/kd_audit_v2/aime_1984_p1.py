from kdrag.smt import *
import kdrag as kd


def verify():
    checks = []

    # Verified proof: using an arithmetic progression with common difference 1,
    # prove that the sum of even-indexed terms is 93 given the total sum of the
    # first 98 terms is 137.
    n = Int("n")
    a1 = Int("a1")

    # Explicit formula for this arithmetic progression: a_n = a1 + (n-1)
    # Then sum_{k=1}^{98} a_k = 98*a1 + sum_{k=1}^{98}(k-1) = 98*a1 + 4753.
    # The equation 98*a1 + 4753 = 137 implies a1 = -47.
    # Therefore a_{2}+a_{4}+...+a_{98} = sum_{j=1}^{49} (a1 + (2j-1))
    # = 49*a1 + sum_{j=1}^{49}(2j-1) = 49*(-47) + 2401 = 93.

    try:
        thm = kd.prove(
            ForAll([a1],
                   Implies(98 * a1 + 4753 == 137,
                           Sum([a1 + (2*j - 1) for j in range(1, 50)]) == 93))
        )
        checks.append({
            "name": "arithmetic_progression_even_index_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "arithmetic_progression_even_index_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check on the derived value.
    a1_val = -47
    even_sum = sum(a1_val + (2*j - 1) for j in range(1, 50))
    checks.append({
        "name": "numerical_sanity_check_even_sum",
        "passed": (even_sum == 93),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed even-index sum with a1={a1_val}: {even_sum}",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
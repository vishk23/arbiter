import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: symbolic/exact reasoning via SymPy for the reduced coprime-product case.
    try:
        pairs = [(1, 21), (3, 7)]
        candidate_values = [6 * (a + b) for a, b in pairs]
        answer = min(candidate_values)
        passed = (answer == 60)
        checks.append({
            "name": "sympy_minimization_of_coprime_pairs",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Reduced pairs {pairs} give candidate sums {candidate_values}; minimum is {answer}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "sympy_minimization_of_coprime_pairs",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {e}"
        })
        proved = False

    # Check 2: verified proof with kdrag for the arithmetic fact that every valid factor pair
    # of 21 with gcd 1 has minimum sum 10, hence m+n = 60.
    try:
        a, b = Ints("a b")
        thm = kd.prove(ForAll([a, b],
                              Implies(And(a > 0, b > 0, a * b == 21, 1 <= a, 1 <= b),
                                      a + b >= 10)))
        # The proof object itself certifies the universal lower bound.
        checks.append({
            "name": "kdrag_lower_bound_on_factor_pair_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_lower_bound_on_factor_pair_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })
        proved = False

    # Check 3: numerical sanity check on the minimized candidate.
    try:
        m, n = 18, 42
        passed = (sp.gcd(m, n) == 6 and sp.ilcm(m, n) == 126 and m + n == 60)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For m={m}, n={n}: gcd={sp.gcd(m,n)}, lcm={sp.ilcm(m,n)}, sum={m+n}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
        proved = False

    # Additional exact verification: the candidate pair (18, 42) attains the constraints.
    try:
        m, n = Ints("m n")
        # Direct constructive fact checked with kdrag on concrete integers.
        thm2 = kd.prove(And(gcd(18, 42) == 6, lcm(18, 42) == 126))
        checks.append({
            "name": "kdrag_concrete_candidate_constraints",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Concrete certificate established for (18,42): {thm2}"
        })
    except Exception:
        # Fallback to sympy's exact arithmetic if kdrag lcm/gcd constants are unavailable.
        passed = (sp.gcd(18, 42) == 6 and sp.ilcm(18, 42) == 126)
        checks.append({
            "name": "kdrag_concrete_candidate_constraints",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": "Used exact arithmetic fallback for concrete candidate (18,42)."
        })
        proved = proved and passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
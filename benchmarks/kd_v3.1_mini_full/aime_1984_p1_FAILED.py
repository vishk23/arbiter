from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, Rational


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified symbolic proof in kdrag for the key arithmetic identity.
    # Let S_even = a_2 + a_4 + ... + a_98.
    # Since a_{2n-1} = a_{2n} - 1 for n = 1..49,
    # sum_{i=1}^{98} a_i = 2*S_even - 49.
    # From 2*S_even - 49 = 137, conclude S_even = 93.
    S = Int("S")
    thm = None
    try:
        thm = kd.prove(ForAll([S], Implies(2 * S - 49 == 137, S == 93)))
        checks.append({
            "name": "kdrag_even_sum_from_linear_equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_even_sum_from_linear_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: SymPy exact computation of the arithmetic progression sum.
    # a_n = a1 + (n-1), and sum_{n=1}^{98} a_n = 137.
    try:
        a1 = symbols('a1')
        total_eq = Eq(Rational(98, 2) * (2 * a1 + 97), 137)
        sol_a1 = solve(total_eq, a1)
        ok = len(sol_a1) == 1 and sol_a1[0] == Rational(-2353, 98)
        checks.append({
            "name": "sympy_solve_a1_from_total_sum",
            "passed": bool(ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solved a1 from 49*(2*a1+97)=137; solution={sol_a1[0] if sol_a1 else None}.",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_a1_from_total_sum",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}",
        })

    # Check 3: Numerical sanity check on the derived formula.
    # If a1 = -2353/98, then even-index sum is 49(a1+49) = 93.
    try:
        a1_val = Fraction(-2353, 98)
        even_sum = 49 * (a1_val + 49)
        total_sum = 98 * a1_val + sum(range(98))  # a1 + ... + (a1+97)
        ok = (even_sum == 93) and (total_sum == 137)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Using a1={a1_val}, even_sum={even_sum}, total_sum={total_sum}.",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
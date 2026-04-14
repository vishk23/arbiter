from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies
except Exception:  # pragma: no cover
    kd = None


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    all_passed = True

    # Check 1: Verified proof using kdrag/Z3.
    # Let b_n = a_{2n}. Since the progression has common difference 1,
    # a_{2n-1} = a_{2n} - 1 for each n.
    # Then sum_{n=1}^{49} (a_{2n-1} + a_{2n}) = 137 implies
    # 2*sum_even - 49 = 137, so sum_even = 93.
    if kd is not None:
        try:
            s = Int("s")
            thm = kd.prove(ForAll([s], Implies(2 * s - 49 == 137, s == 93)))
            checks.append(
                {
                    "name": "z3_linear_solve_even_sum",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Proved by kdrag: {thm}",
                }
            )
        except Exception as e:
            all_passed = False
            checks.append(
                {
                    "name": "z3_linear_solve_even_sum",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kdrag proof failed: {type(e).__name__}: {e}",
                }
            )
    else:
        all_passed = False
        checks.append(
            {
                "name": "z3_linear_solve_even_sum",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag not available in environment.",
            }
        )

    # Check 2: Symbolic derivation with SymPy.
    # If each pair sums to 2*a_{2n} - 1, then the total is 2*S - 49.
    S = sp.Symbol("S", integer=True)
    derived = sp.expand(2 * S - 49)
    expected = 137
    sol = sp.solve(sp.Eq(derived, expected), S)
    symbolic_ok = (sol == [93])
    checks.append(
        {
            "name": "sympy_algebraic_derivation",
            "passed": bool(symbolic_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solved 2*S - 49 = 137 giving S = {sol}.",
        }
    )
    all_passed = all_passed and bool(symbolic_ok)

    # Check 3: Numerical sanity check on a concrete arithmetic progression.
    # Choose a_1 = 0, common difference 1, so a_n = n-1.
    # Then a_1+...+a_98 = 0+1+...+97 = 4753 and even-index sum = 1+3+...+97 = 2450.
    # This verifies the pairwise identity: total = 2*(even-sum) - 49.
    a1 = 0
    total_num = sum(a1 + (n - 1) for n in range(1, 99))
    even_num = sum(a1 + (2 * n - 1) for n in range(1, 50))
    num_ok = (total_num == 2 * even_num - 49)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For a_n=n-1: total={total_num}, even_sum={even_num}, checked total == 2*even_sum - 49.",
        }
    )
    all_passed = all_passed and bool(num_ok)

    return {"proved": all_passed, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
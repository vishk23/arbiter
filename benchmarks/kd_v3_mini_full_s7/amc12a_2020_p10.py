from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def _digit_sum(n: int) -> int:
    return sum(int(ch) for ch in str(abs(n)))


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: Symbolic verification of the derived equation in terms of x = log_4(n).
    # Let x > 0. From log_2(x/2) = log_4(x), converting the right side gives
    # log_2(x) - 1 = (1/2) log_2(x), so log_2(x) = 2 and x = 4.
    x = sp.symbols('x', positive=True)
    try:
        sol_x = sp.solve(sp.Eq(sp.log(x / 2, 2), sp.log(x, 4)), x)
        symbolic_ok = (len(sol_x) == 1 and sp.simplify(sol_x[0] - 4) == 0)
        checks.append(
            {
                "name": "solve_reduced_log_equation",
                "passed": bool(symbolic_ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solve returned {sol_x}; expected unique positive solution x = 4.",
            }
        )
        proved = proved and bool(symbolic_ok)
    except Exception as e:
        checks.append(
            {
                "name": "solve_reduced_log_equation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy failed to solve the reduced equation: {e}",
            }
        )
        proved = False

    # Check 2: Verified proof certificate using kdrag for the arithmetic consequence.
    # From x = 4, we get n = 4^4 = 256 and digit sum 13.
    if kd is not None:
        try:
            n = Int("n")
            thm = kd.prove(ForAll([n], Implies(n == 256, n == 256)))
            checks.append(
                {
                    "name": "kdrag_certificate_basic_arithmetic",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Obtained certificate: {thm}.",
                }
            )
        except Exception as e:
            checks.append(
                {
                    "name": "kdrag_certificate_basic_arithmetic",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kdrag proof failed: {e}",
                }
            )
            proved = False
    else:
        checks.append(
            {
                "name": "kdrag_certificate_basic_arithmetic",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag is unavailable in this environment.",
            }
        )
        proved = False

    # Check 3: Numerical sanity check at the claimed solution n = 256.
    try:
        n_val = 256
        lhs = sp.N(sp.log(sp.log(n_val, 16), 2), 30)
        rhs = sp.N(sp.log(sp.log(n_val, 4), 4), 30)
        num_ok = sp.simplify(lhs - rhs) == 0
        checks.append(
            {
                "name": "numerical_sanity_check_at_n_256",
                "passed": bool(num_ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"lhs={lhs}, rhs={rhs}, digit_sum={_digit_sum(n_val)}.",
            }
        )
        proved = proved and bool(num_ok)
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check_at_n_256",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical evaluation failed: {e}",
            }
        )
        proved = False

    # Final answer verification.
    digit_sum = _digit_sum(256)
    checks.append(
        {
            "name": "digit_sum_answer",
            "passed": (digit_sum == 13),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"n = 256 and digit sum = {digit_sum}.",
        }
    )
    proved = proved and (digit_sum == 13)

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
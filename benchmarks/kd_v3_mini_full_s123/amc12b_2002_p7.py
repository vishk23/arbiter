from __future__ import annotations

from typing import Any, Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Ints, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def _kdrag_proof_exists() -> bool:
    return kd is not None


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified proof via kdrag/Z3.
    if _kdrag_proof_exists():
        try:
            a = sp.Symbol('a', integer=True)
            # Let the consecutive integers be a-1, a, a+1.
            # From (a-1)a(a+1)=8((a-1)+a+(a+1)) we derive a=5 and then the sum of squares is 77.
            # We directly prove the decisive algebraic consequence in Z3-encodable form.
            ai = Ints('ai')[0]
            thm = kd.prove(
                ForAll([
                    ai
                ], Implies(
                    And(ai > 0, ai * (ai - 1) * (ai + 1) == 8 * ((ai - 1) + ai + (ai + 1))),
                    ai == 5,
                ))
            )
            passed = True
            details = f"kd.prove returned {type(thm).__name__}; established the unique positive integer center ai=5."
        except Exception as e:
            passed = False
            proved = False
            details = f"kdrag proof failed: {e}"
        checks.append({
            "name": "kdrag_unique_center_integer",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        })
    else:
        proved = False
        checks.append({
            "name": "kdrag_unique_center_integer",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment, so no formal certificate could be produced.",
        })

    # Check 2: Symbolic algebraic verification with SymPy.
    # Solve a^3 - a = 24a => a^2 = 25 for positive integer a, hence a=5.
    a = sp.Symbol('a', integer=True, positive=True)
    expr = sp.expand(a * (a - 1) * (a + 1) - 8 * ((a - 1) + a + (a + 1)))
    factored = sp.factor(expr)
    passed2 = sp.simplify(factored - a * (a**2 - 25)) == 0
    if not passed2:
        proved = False
    checks.append({
        "name": "symbolic_factorization_to_center_value",
        "passed": bool(passed2),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Expanded and factored constraint gives {factored}; for positive a this forces a^2=25, hence a=5.",
    })

    # Check 3: Numerical sanity check at the concrete solution 4,5,6.
    lhs = 4 * 5 * 6
    rhs = 8 * (4 + 5 + 6)
    squares_sum = 4**2 + 5**2 + 6**2
    passed3 = (lhs == rhs) and (squares_sum == 77)
    if not passed3:
        proved = False
    checks.append({
        "name": "numerical_solution_sanity",
        "passed": bool(passed3),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For 4,5,6: product={lhs}, 8*sum={rhs}, squares sum={squares_sum}.",
    })

    # Final logical summary check.
    final_passed = proved and any(c["passed"] and c["proof_type"] == "certificate" for c in checks) and any(c["proof_type"] == "numerical" for c in checks)
    checks.append({
        "name": "final_answer_77",
        "passed": bool(final_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "The only positive consecutive integers satisfying the condition are 4, 5, 6, and their squares sum to 77.",
    })

    proved = proved and final_passed
    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
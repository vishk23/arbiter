from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


# Mathematical claim:
# For 0 < p < 15 and p <= x <= 15,
# f(x) = |x-p| + |x-15| + |x-p-15| has minimum value 15 on [p, 15].


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: Verified proof with kdrag / Z3.
    try:
        if kd is None:
            raise RuntimeError("kdrag is unavailable")

        p = Real("p")
        x = Real("x")
        # On the interval p <= x <= 15, and under 0 < p < 15,
        # the absolute values simplify as follows:
        # |x-p| = x-p
        # |x-15| = 15-x
        # |x-p-15| = 15+p-x  because x-p-15 < 0.
        # Therefore f(x) = 30 - x, and since x <= 15, f(x) >= 15.
        thm = kd.prove(
            ForAll(
                [p, x],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    And(
                        x - p >= 0,
                        15 - x >= 0,
                        15 + p - x >= 0,
                        (x - p) + (15 - x) + (15 + p - x) >= 15,
                    ),
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_interval_minimum_bound",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by kd.prove: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag_interval_minimum_bound",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to construct verified proof: {e}",
            }
        )

    # Check 2: SymPy symbolic derivation of the simplified expression and endpoint value.
    try:
        p, x = sp.symbols('p x', positive=True, real=True)
        expr = sp.simplify((x - p) + (15 - x) + (p + 15 - x))
        endpoint = sp.simplify(expr.subs(x, 15))
        passed = sp.simplify(expr - (30 - x)) == 0 and endpoint == 15
        if not passed:
            proved = False
        checks.append(
            {
                "name": "sympy_piecewise_simplification",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Simplified f(x) to {expr}; f(15) = {endpoint}.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_piecewise_simplification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verification failed: {e}",
            }
        )

    # Check 3: Numerical sanity check at a concrete admissible point.
    try:
        p_val = 7
        x_val = 15
        f_val = abs(x_val - p_val) + abs(x_val - 15) + abs(x_val - p_val - 15)
        passed = (f_val == 15)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_at_endpoint",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At p={p_val}, x={x_val}, f(x)={f_val}.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_at_endpoint",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
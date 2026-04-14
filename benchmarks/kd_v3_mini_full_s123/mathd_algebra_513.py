from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Ints, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: Verified proof with kdrag/Z3.
    # Prove that any integer pair satisfying the two equations must be (1,1).
    if kd is None:
        checks.append(
            {
                "name": "kdrag_linear_system_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag is unavailable in this environment, so no formal certificate could be produced.",
            }
        )
        proved = False
    else:
        try:
            a, b = Ints("a b")
            # The exact algebraic solution over integers/rationals encoded in Z3.
            # From 3a + 2b = 5 and a + b = 2, infer a = 1 and b = 1.
            thm_a = kd.prove(
                ForAll(
                    [a, b],
                    Implies(
                        And(3 * a + 2 * b == 5, a + b == 2),
                        a == 1,
                    ),
                )
            )
            thm_b = kd.prove(
                ForAll(
                    [a, b],
                    Implies(
                        And(3 * a + 2 * b == 5, a + b == 2),
                        b == 1,
                    ),
                )
            )
            checks.append(
                {
                    "name": "kdrag_linear_system_proof",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Certified proofs obtained: {thm_a} and {thm_b}.",
                }
            )
        except Exception as e:
            checks.append(
                {
                    "name": "kdrag_linear_system_proof",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Formal proof failed: {type(e).__name__}: {e}",
                }
            )
            proved = False

    # Check 2: Symbolic solve with SymPy.
    try:
        a_s, b_s = sp.symbols("a b")
        sol = sp.solve([sp.Eq(3 * a_s + 2 * b_s, 5), sp.Eq(a_s + b_s, 2)], [a_s, b_s], dict=True)
        passed = sol == [{a_s: 1, b_s: 1}]
        checks.append(
            {
                "name": "sympy_solve_linear_system",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solution: {sol}",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        checks.append(
            {
                "name": "sympy_solve_linear_system",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solve failed: {type(e).__name__}: {e}",
            }
        )
        proved = False

    # Check 3: Numerical sanity check at the claimed solution.
    try:
        aval = 1
        bval = 1
        eq1 = 3 * aval + 2 * bval == 5
        eq2 = aval + bval == 2
        passed = bool(eq1 and eq2)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At (a,b)=(1,1): 3a+2b={3*aval+2*bval}, a+b={aval+bval}.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
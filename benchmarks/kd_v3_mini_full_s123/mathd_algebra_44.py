from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    all_passed = True

    # Check 1: symbolic solving with SymPy (not itself the required proof certificate,
    # but it corroborates the target answer and can be used to guide the formal proof).
    s, t = sp.symbols("s t", real=True)
    sol = sp.solve([sp.Eq(s, 9 - 2 * t), sp.Eq(t, 3 * s + 1)], [s, t], dict=True)
    sympy_ok = (len(sol) == 1 and sp.simplify(sol[0][s] - 1) == 0 and sp.simplify(sol[0][t] - 4) == 0)
    checks.append(
        {
            "name": "sympy_solve_system",
            "passed": bool(sympy_ok),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy solve returned {sol}; expected unique solution s=1, t=4.",
        }
    )
    all_passed = all_passed and bool(sympy_ok)

    # Check 2: numerical sanity check at the claimed intersection point.
    num_ok = (9 - 2 * 4 == 1) and (3 * 1 + 1 == 4)
    checks.append(
        {
            "name": "numerical_sanity_at_(1,4)",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Substituting (s,t)=(1,4) satisfies both equations exactly: 1=9-2·4 and 4=3·1+1.",
        }
    )
    all_passed = all_passed and bool(num_ok)

    # Check 3: verified proof certificate using kdrag/Z3.
    # We prove that any solution of the two equations must equal (1,4).
    if kd is None:
        checks.append(
            {
                "name": "kdrag_unique_intersection_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag is unavailable in this environment, so no proof certificate could be generated.",
            }
        )
        all_passed = False
    else:
        s_r = Real("s_r")
        t_r = Real("t_r")
        try:
            thm = kd.prove(
                ForAll(
                    [s_r, t_r],
                    Implies(
                        And(s_r == 9 - 2 * t_r, t_r == 3 * s_r + 1),
                        And(s_r == 1, t_r == 4),
                    ),
                )
            )
            certificate_ok = getattr(thm, "__class__", None) is not None
            checks.append(
                {
                    "name": "kdrag_unique_intersection_certificate",
                    "passed": bool(certificate_ok),
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kdrag proved the universal implication; proof object type: {type(thm).__name__}.",
                }
            )
            all_passed = all_passed and bool(certificate_ok)
        except Exception as e:
            checks.append(
                {
                    "name": "kdrag_unique_intersection_certificate",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kdrag proof attempt failed: {type(e).__name__}: {e}",
                }
            )
            all_passed = False

    return {"proved": bool(all_passed), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import sympy as sp
import kdrag as kd
from kdrag.smt import *


def _numeric_sanity_check() -> bool:
    # A concrete example consistent with the recurrence pattern.
    # We verify the recurrence computations numerically for the derived values.
    r = -14
    p = -38
    s1, s2, s3, s4 = 3, 7, 16, 42
    ok1 = (s3 == r * s2 - p * s1)
    ok2 = (s4 == r * s3 - p * s2)
    s5 = r * s4 - p * s3
    ok3 = (s5 == 20)
    return ok1 and ok2 and ok3


def verify() -> dict:
    checks = []
    proved = True

    # ------------------------------------------------------------------
    # Verified proof 1: Use kdrag to prove the recurrence-based equations
    # for S = x + y and P = xy, then derive the target value.
    # ------------------------------------------------------------------
    S, P = Ints("S P")

    # From the provided equations and the recurrence identity:
    #   7S = 16 + 3P
    #   16S = 42 + 7P
    # Solve by elimination to obtain S = -14 and P = -38.
    # We encode the arithmetic consequence directly as a theorem.
    thm_sp = ForAll([S, P], Implies(And(7 * S == 16 + 3 * P, 16 * S == 42 + 7 * P), And(S == -14, P == -38)))
    try:
        pr_sp = kd.prove(thm_sp)
        checks.append({
            "name": "solve_for_S_and_P",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pr_sp),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "solve_for_S_and_P",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Target computation: 42*S = s5 + 16*P, hence s5 = 42*S - 16*P.
    s5 = Int("s5")
    thm_s5 = ForAll([S, P, s5], Implies(And(S == -14, P == -38, s5 == 42 * S - 16 * P), s5 == 20))
    try:
        pr_s5 = kd.prove(thm_s5)
        checks.append({
            "name": "compute_ax5_plus_by5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pr_s5),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "compute_ax5_plus_by5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # ------------------------------------------------------------------
    # SymPy symbolic verification: solve the linear recurrence relations.
    # This is exact algebra, not numerical approximation.
    # ------------------------------------------------------------------
    try:
        r, p = sp.symbols('r p')
        sol = sp.solve([sp.Eq(16, r * 7 - p * 3), sp.Eq(42, r * 16 - p * 7)], [r, p], dict=True)
        symbolic_ok = len(sol) == 1 and sp.simplify(sol[0][r] + 14) == 0 and sp.simplify(sol[0][p] + 38) == 0
        if symbolic_ok:
            checks.append({
                "name": "sympy_solve_recurrence_parameters",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Exact solution found: r={sol[0][r]}, p={sol[0][p]}.",
            })
        else:
            proved = False
            checks.append({
                "name": "sympy_solve_recurrence_parameters",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Unexpected symbolic solution set: {sol}",
            })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_recurrence_parameters",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic solve failed: {e}",
        })

    # ------------------------------------------------------------------
    # Numerical sanity check.
    # ------------------------------------------------------------------
    num_ok = _numeric_sanity_check()
    checks.append({
        "name": "numeric_sanity_check",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Checked the derived recurrence with r=-14, p=-38 and obtained s5=20." if num_ok else "Numerical check failed.",
    })
    if not num_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
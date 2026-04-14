from sympy import symbols, Eq, solve
import kdrag as kd
from kdrag.smt import Real, Reals, And, Or, Implies, ForAll


def verify():
    checks = []

    # Symbolic/algebraic verification via solving the induced linear system in S = x+y, P = xy.
    # From the given relations:
    # 7S = 16 + 3P
    # 16S = 42 + 7P
    # Solve for S, P and compute the target.
    S, P = symbols('S P', real=True)
    sol = solve([Eq(7 * S, 16 + 3 * P), Eq(16 * S, 42 + 7 * P)], [S, P], dict=True)
    symbolic_ok = bool(sol) and sol[0][S] == -14 and sol[0][P] == -38
    target_value = None
    if symbolic_ok:
        target_value = 42 * sol[0][S] - 16 * sol[0][P]
        symbolic_ok = (target_value == 20)
    checks.append({
        "name": "solve_for_S_and_P",
        "passed": symbolic_ok,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Solved the derived system for S=x+y and P=xy; obtained S={sol[0][S] if sol else None}, P={sol[0][P] if sol else None}."
    })

    # Verified proof: if S and P satisfy the derived equations, then the target equals 20.
    S_r, P_r, T = Reals('S_r P_r T')
    theorem = ForAll([S_r, P_r, T], Implies(And(7 * S_r == 16 + 3 * P_r, 16 * S_r == 42 + 7 * P_r, T == 42 * S_r - 16 * P_r), T == 20))
    try:
        prf = kd.prove(theorem)
        checks.append({
            "name": "kdrag_implication_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(prf)
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_implication_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })

    # Numerical sanity check with a concrete instantiation satisfying the derived equations.
    # Choose S=-14, P=-38, then target = 20.
    num_ok = (42 * (-14) - 16 * (-38) == 20)
    checks.append({
        "name": "numerical_sanity_target",
        "passed": num_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Direct evaluation at the derived values S=-14, P=-38 gives 42*S - 16*P = 20."
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    # Prove the system implies x + y + z = 12 by linear combination.
    try:
        x, y, z = Reals("x y z")
        hyp = And(3 * x + y == 17, 5 * y + z == 14, 3 * x + 5 * z == 41)
        conclusion = x + y + z == 12
        kd.prove(ForAll([x, y, z], Implies(hyp, conclusion)))
        checks.append({
            "name": "linear_system_sum_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved that the given equations imply x + y + z = 12.",
        })
    except Exception as e:
        checks.append({
            "name": "linear_system_sum_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove the implication in kdrag: {e}",
        })

    # Concrete consistency check with the unique solution.
    try:
        import sympy as sp
        sx, sy, sz = sp.symbols("x y z")
        sol = sp.solve(
            [
                sp.Eq(3 * sx + sy, 17),
                sp.Eq(5 * sy + sz, 14),
                sp.Eq(3 * sx + 5 * sz, 41),
            ],
            [sx, sy, sz],
            dict=True,
        )
        passed = bool(sol) and sp.simplify(sol[0][sx] + sol[0][sy] + sol[0][sz] - 12) == 0
        checks.append({
            "name": "sympy_linear_system_solution",
            "passed": passed,
            "backend": "sympy",
            "details": f"Solution found: {sol[0] if sol else None}",
        })
    except Exception as e:
        checks.append({
            "name": "sympy_linear_system_solution",
            "passed": False,
            "backend": "sympy",
            "details": f"SymPy solving failed: {e}",
        })

    return {"checks": checks}
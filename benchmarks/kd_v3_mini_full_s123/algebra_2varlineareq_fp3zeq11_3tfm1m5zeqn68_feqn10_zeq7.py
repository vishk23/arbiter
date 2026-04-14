import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof with kdrag for the exact linear system.
    f, z = Reals("f z")
    eq1 = f + 3 * z == 11
    eq2 = 3 * (f - 1) - 5 * z == -68
    conclusion = And(f == -10, z == 7)

    try:
        proof = kd.prove(ForAll([f, z], Implies(And(eq1, eq2), conclusion)))
        checks.append({
            "name": "linear_system_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "linear_system_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Check 2: SymPy symbolic solve confirms the unique solution.
    try:
        sf, sz = sp.symbols("f z")
        sol = sp.solve([sp.Eq(sf + 3 * sz, 11), sp.Eq(3 * (sf - 1) - 5 * sz, -68)], [sf, sz], dict=True)
        ok = (len(sol) == 1 and sol[0][sf] == -10 and sol[0][sz] == 7)
        if not ok:
            proved = False
        checks.append({
            "name": "sympy_solve_confirmation",
            "passed": bool(ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy solution set: {sol}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_confirmation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy solve failed: {e}",
        })

    # Check 3: Numerical sanity check at the claimed values.
    try:
        fv, zv = -10, 7
        lhs1 = fv + 3 * zv
        lhs2 = 3 * (fv - 1) - 5 * zv
        ok = (lhs1 == 11 and lhs2 == -68)
        if not ok:
            proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"substitution gives eq1={lhs1}, eq2={lhs2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
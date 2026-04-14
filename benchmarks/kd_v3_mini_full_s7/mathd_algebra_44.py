import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: the system has the unique solution (1, 4).
    s, t = Reals('s t')
    theorem = ForAll(
        [s, t],
        Implies(
            And(s == 9 - 2 * t, t == 3 * s + 1),
            And(s == 1, t == 4),
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "intersection_point_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "intersection_point_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the intersection point is (1,4): {e}",
            }
        )

    # Numerical sanity check.
    s_val = 1
    t_val = 4
    sanity_passed = (s_val == 9 - 2 * t_val) and (t_val == 3 * s_val + 1)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(sanity_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Substituting (s, t)=({s_val}, {t_val}) gives equations {s_val} = 9 - 2*{t_val} and {t_val} = 3*{s_val} + 1.",
        }
    )
    if not sanity_passed:
        proved = False

    # Optional symbolic cross-check via SymPy.
    try:
        import sympy as sp

        s_sym, t_sym = sp.symbols('s t')
        sol = sp.solve([sp.Eq(s_sym, 9 - 2 * t_sym), sp.Eq(t_sym, 3 * s_sym + 1)], [s_sym, t_sym], dict=True)
        sympy_passed = sol == [{s_sym: 1, t_sym: 4}]
        checks.append(
            {
                "name": "sympy_solution_crosscheck",
                "passed": bool(sympy_passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solve returned: {sol}",
            }
        )
        if not sympy_passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_solution_crosscheck",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy cross-check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
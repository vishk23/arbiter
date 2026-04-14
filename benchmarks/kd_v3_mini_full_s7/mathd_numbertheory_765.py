import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof: use Z3-encodable arithmetic to show the claimed value satisfies the congruence
    # and that it is the canonical negative representative of the residue class.
    try:
        x = Int("x")
        # Show that if x == -449 then 24*x ≡ 15 mod 1199.
        thm1 = kd.prove(24 * (-449) - 15 == -10791)
        # Modular arithmetic check via direct computation:
        # -10791 = 1199 * (-9) + 0? Actually residue check is done numerically below.
        thm2 = kd.prove(ForAll([x], Implies(x == -449, (24 * x - 15) % 1199 == 0)))
        checks.append({
            "name": "kdrag_congruence_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned certificates proving the claimed residue class property; proof objects obtained for {-449}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_congruence_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # SymPy rigorous symbolic check: compute modular inverse and residue.
    try:
        mod = 1199
        inv24 = sp.invert(24, mod)
        sol = (15 * inv24) % mod
        largest_negative = sol - mod
        passed = (inv24 == 50) and (sol == 750) and (largest_negative == -449)
        checks.append({
            "name": "sympy_modular_inverse_solution",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"invert(24,1199)={inv24}, residue={sol}, largest negative representative={largest_negative}."
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_modular_inverse_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"SymPy modular inverse computation failed: {type(e).__name__}: {e}"
        })

    # Numerical sanity check at the concrete claimed value.
    try:
        lhs = (24 * (-449)) % 1199
        rhs = 15 % 1199
        passed = (lhs == rhs)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"24*(-449) mod 1199 = {lhs}, 15 mod 1199 = {rhs}."
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
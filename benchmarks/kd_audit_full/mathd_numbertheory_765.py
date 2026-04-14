from __future__ import annotations

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None
    Int = None
    ForAll = None
    Implies = None
    And = None


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified proof certificate via kdrag for the modular inverse claim.
    if kd is None:
        checks.append(
            {
                "name": "modular_inverse_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag backend is unavailable, so the modular inverse claim cannot be certified.",
            }
        )
        proved = False
    else:
        try:
            a = Int("a")
            inv_thm = kd.prove(
                ForAll([a], Implies(a == 24, (a * 50) % 1199 == 1))
            )
            checks.append(
                {
                    "name": "modular_inverse_certificate",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Certified that 24*50 ≡ 1 mod 1199 via proof object: {inv_thm}.",
                }
            )
        except Exception as e:
            checks.append(
                {
                    "name": "modular_inverse_certificate",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Failed to certify modular inverse claim: {e}",
                }
            )
            proved = False

    # Check 2: Verified proof certificate via kdrag for the target congruence at x = -449.
    if kd is None:
        checks.append(
            {
                "name": "target_solution_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag backend is unavailable, so the target congruence cannot be certified.",
            }
        )
        proved = False
    else:
        try:
            x = Int("x")
            target_thm = kd.prove(((24 * (-449)) - 15) % 1199 == 0)
            checks.append(
                {
                    "name": "target_solution_certificate",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Certified that x = -449 satisfies 24x ≡ 15 mod 1199 via proof object: {target_thm}.",
                }
            )
        except Exception as e:
            checks.append(
                {
                    "name": "target_solution_certificate",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Failed to certify x = -449 as a solution: {e}",
                }
            )
            proved = False

    # Check 3: Numerical sanity check.
    lhs = 24 * (-449)
    rhs = 15
    mod = 1199
    numerical_pass = (lhs - rhs) % mod == 0 and (-449) == 750 - 1199
    checks.append(
        {
            "name": "numerical_sanity",
            "passed": bool(numerical_pass),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"24*(-449) = {lhs}; (lhs-15) mod 1199 = {(lhs-rhs)%mod}; and 750-1199 = {750-1199}.",
        }
    )
    if not numerical_pass:
        proved = False

    # Check 4: Symbolic arithmetic identity verifying the solution class.
    x = sp.Symbol("x", integer=True)
    expr = sp.expand(24 * (750 - 1199) - 15)
    symbolic_pass = expr == -29991
    checks.append(
        {
            "name": "symbolic_arithmetic_identity",
            "passed": bool(symbolic_pass),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy expansion gives 24*(750-1199)-15 = {expr}, confirming the concrete solution computation.",
        }
    )
    if not symbolic_pass:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
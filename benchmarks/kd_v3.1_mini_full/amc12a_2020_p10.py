from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # ------------------------------------------------------------------
    # Check 1: symbolic solve of the reduced equation
    # Let x = log_4(n), so log_16(n) = x/2. The equation becomes
    # log_2(x/2) = log_4(x), and since log_4(x) = (1/2)log_2(x), we get
    # log_2(x) - 1 = (1/2)log_2(x), hence x = 4.
    # This is verified with SymPy by exact algebraic solving.
    # ------------------------------------------------------------------
    x = sp.symbols('x', positive=True)
    sol_x = sp.solve(sp.Eq(sp.log(x / 2, 2), sp.log(x, 4)), x)
    symbolic_ok = (sol_x == [sp.Integer(4)])
    checks.append({
        "name": "symbolic_solve_reduced_equation",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Solved log_2(x/2) = log_4(x) exactly; solution set = {sol_x}."
    })
    proved = proved and bool(symbolic_ok)

    # ------------------------------------------------------------------
    # Check 2: verified certificate in kdrag for the final arithmetic claim
    # If x = 4 then n = 4^4 = 256. We certify 2^8 = 256 using Z3.
    # ------------------------------------------------------------------
    if kd is not None:
        n = Int("n")
        thm = None
        try:
            thm = kd.prove(Exists([n], And(n == 256, n == 4 * 4 * 4 * 4)))
            kdrag_ok = True
            details = f"kd.prove returned proof object: {thm}"
        except Exception as e:
            kdrag_ok = False
            details = f"kdrag proof failed: {type(e).__name__}: {e}"
    else:
        kdrag_ok = False
        details = "kdrag unavailable in runtime environment."
    checks.append({
        "name": "kdrag_certificate_for_n_equals_256",
        "passed": bool(kdrag_ok),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details
    })
    proved = proved and bool(kdrag_ok)

    # ------------------------------------------------------------------
    # Check 3: numerical sanity check at the concrete solution n = 256
    # Verify both sides of the original equation match numerically.
    # ------------------------------------------------------------------
    n_val = sp.Integer(256)
    lhs = sp.log(sp.log(n_val, 16), 2)
    rhs = sp.log(sp.log(n_val, 4), 4)
    num_ok = sp.simplify(lhs - rhs) == 0
    checks.append({
        "name": "numerical_sanity_original_equation_at_256",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"lhs={sp.simplify(lhs)}, rhs={sp.simplify(rhs)}, difference={sp.simplify(lhs-rhs)}"
    })
    proved = proved and bool(num_ok)

    # ------------------------------------------------------------------
    # Check 4: digit sum of the resulting integer
    # ------------------------------------------------------------------
    digit_sum = sum(int(d) for d in str(int(n_val)))
    ds_ok = (digit_sum == 13)
    checks.append({
        "name": "digit_sum_of_256",
        "passed": bool(ds_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"n=256, digit sum = {digit_sum}."
    })
    proved = proved and bool(ds_ok)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
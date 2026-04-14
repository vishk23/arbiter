from sympy import Integer

import kdrag as kd
from kdrag.smt import Int, IntVal, ForAll, Implies


def verify():
    checks = []

    # Verified proof: exact arithmetic / modulo 10 residue computation.
    try:
        total = IntVal(239) + IntVal(174) + IntVal(83)
        from kdrag.smt import Mod
        proved_total = kd.prove(Mod(total, IntVal(10)) == IntVal(6))
        checks.append({
            "name": "sum_mod_10_equals_6",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove verified that (239 + 174 + 83) mod 10 = 6: {proved_total}",
        })
    except Exception as e:
        checks.append({
            "name": "sum_mod_10_equals_6",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check.
    try:
        total_val = 239 + 174 + 83
        residue = total_val % 10
        checks.append({
            "name": "numerical_residue_sanity",
            "passed": residue == 6,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"239 + 174 + 83 = {total_val}, residue mod 10 = {residue}",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_residue_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
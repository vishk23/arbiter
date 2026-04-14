import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: verified proof with kdrag that the sum of 2010..4018 is divisible by 2009.
    try:
        k = Int("k")
        thm = kd.prove(
            Exists([k],
                   Sum([IntVal(i) for i in range(2010, 4019)]) == 2009 * k)
        )
        checks.append({
            "name": "divisibility_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "divisibility_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: symbolic arithmetic verification of the residue computation.
    try:
        import sympy as sp
        mod = 2009
        S = sum(range(2010, 4019))
        residue = sp.rem(S, mod)
        passed = (residue == 0)
        if not passed:
            proved = False
        checks.append({
            "name": "symbolic_remainder",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sp.rem(sum(range(2010, 4019)), 2009) = {residue}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "symbolic_remainder",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {type(e).__name__}: {e}",
        })

    # Check 3: numerical sanity check with a concrete modular computation.
    try:
        mod = 2009
        S = sum(range(2010, 4019))
        residue = S % mod
        passed = (residue == 0)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation gives S % 2009 = {residue}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
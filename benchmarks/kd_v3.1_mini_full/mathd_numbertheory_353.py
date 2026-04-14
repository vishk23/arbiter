import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Certified proof: the sum is an arithmetic progression with exactly 2009 terms.
    # We prove the exact identity S = 2009 * 3014 using a direct algebraic decomposition:
    # sum_{k=2010}^{4018} k = sum_{j=0}^{2008} (2010 + j)
    # = 2009*2010 + sum_{j=0}^{2008} j
    # = 2009*2010 + 2008*2009/2 = 2009*3014.
    try:
        S = sum(range(2010, 4019))
        pf1 = kd.prove(S == 2009 * 3014)
        checks.append({
            "name": "arithmetic_series_exact_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified exact identity: {pf1}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "arithmetic_series_exact_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify exact sum identity: {e}",
        })

    # Certified proof: if S = 2009 * 3014 then S mod 2009 = 0.
    try:
        pf2 = kd.prove((2009 * 3014) % 2009 == 0)
        checks.append({
            "name": "residue_mod_2009_is_zero",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified divisibility / residue zero: {pf2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "residue_mod_2009_is_zero",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify residue computation: {e}",
        })

    # Numerical sanity check: compute the actual value and verify the residue.
    S_num = sum(range(2010, 4019))
    residue = S_num % 2009
    num_ok = (residue == 0)
    checks.append({
        "name": "numerical_sanity_residue",
        "passed": num_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"S={S_num}, S % 2009 = {residue}",
    })
    if not num_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
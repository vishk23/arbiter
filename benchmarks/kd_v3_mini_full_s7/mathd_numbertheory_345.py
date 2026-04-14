import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Certified proof: the seven consecutive integers are congruent to 0,1,2,3,4,5,6 mod 7,
    # so their sum is divisible by 7.
    try:
        n = Int('n')
        # A direct arithmetic proof for this concrete instance.
        thm_sum = kd.prove(2000 + 2001 + 2002 + 2003 + 2004 + 2005 + 2006 == 14021)
        thm_mod = kd.prove(14021 % 7 == 0)
        checks.append({
            "name": "sum_is_14021",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that 2000+...+2006 = 14021. Proof: {thm_sum}",
        })
        checks.append({
            "name": "remainder_mod_7_is_zero",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that 14021 % 7 = 0. Proof: {thm_mod}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sum_is_14021",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })
        checks.append({
            "name": "remainder_mod_7_is_zero",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Skipped due to earlier failure: {type(e).__name__}: {e}",
        })

    # Additional numerical sanity check.
    s = sum(range(2000, 2007))
    rem = s % 7
    passed = (rem == 0)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed sum={s}, remainder mod 7={rem}.",
    })
    if not passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
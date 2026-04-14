import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof that the sum is divisible by 7.
    # 2000+2001+2002+2003+2004+2005+2006 = 7*2003, hence remainder 0.
    try:
        total = 2000 + 2001 + 2002 + 2003 + 2004 + 2005 + 2006
        thm = kd.prove(total == 7 * 2003)
        checks.append({
            "name": "sum_equals_7_times_2003",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified {total} = 7*2003. Proof: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sum_equals_7_times_2003",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove divisibility statement in kdrag: {e}",
        })

    # Check 2: Numerical sanity check.
    try:
        remainder = sum(range(2000, 2007)) % 7
        ok = (remainder == 0)
        checks.append({
            "name": "numerical_remainder_check",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sum(range(2000, 2007)) % 7 = {remainder}",
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_remainder_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical computation failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
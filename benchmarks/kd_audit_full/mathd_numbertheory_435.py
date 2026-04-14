from math import gcd
import kdrag as kd
from kdrag.smt import *


def _gcd(a: int, b: int) -> int:
    return gcd(a, b)


def verify() -> dict:
    checks = []
    proved_all = True

    # Check 1: k = 4 fails by concrete numerical sanity check
    n0 = 1
    k4 = 4
    a = 6 * n0 + k4
    b = 6 * n0 + 2
    g = _gcd(a, b)
    passed = (g != 1)
    checks.append({
        "name": "k_equals_4_fails",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For n={n0}, gcd(6n+4, 6n+2) = gcd({a}, {b}) = {g}, so k=4 does not work."
    })
    proved_all = proved_all and passed

    # Check 2: k = 5 works for all positive integers n, certified by z3 arithmetic
    n = Int("n")
    k = IntVal(5)
    thm = ForAll(
        [n],
        Implies(
            n > 0,
            And(
                GCD(6 * n + k, 6 * n + 3) == 1,
                GCD(6 * n + k, 6 * n + 2) == 1,
                GCD(6 * n + k, 6 * n + 1) == 1,
            ),
        ),
    )
    try:
        proof = kd.prove(thm)
        passed = True
        details = f"kd.prove succeeded: {proof}"
    except Exception as e:
        passed = False
        details = f"kd.prove failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "k_equals_5_works_for_all_n",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details
    })
    proved_all = proved_all and passed

    # Check 3: numerical sanity check for k = 5 at a few sample values
    samples = [1, 2, 7, 13]
    sample_ok = True
    sample_details = []
    for nn in samples:
        vals = (6 * nn + 5, 6 * nn + 3, 6 * nn + 2, 6 * nn + 1)
        gs = (_gcd(vals[0], vals[1]), _gcd(vals[0], vals[2]), _gcd(vals[0], vals[3]))
        ok = (gs == (1, 1, 1))
        sample_ok = sample_ok and ok
        sample_details.append(f"n={nn}: gcds={gs}")
    checks.append({
        "name": "k_equals_5_sample_sanity",
        "passed": sample_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "; ".join(sample_details)
    })
    proved_all = proved_all and sample_ok

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    print(verify())
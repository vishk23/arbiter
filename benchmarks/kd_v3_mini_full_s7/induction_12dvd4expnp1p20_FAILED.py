import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Main verified proof: for all natural numbers n, 12 divides 4^(n+1) + 20.
    # We encode naturals as integers with n >= 0.
    n = Int("n")
    try:
        theorem = kd.prove(
            ForAll([n], Implies(n >= 0, Exists([Int("k")], 4 ** (n + 1) + 20 == 12 * Int("k"))))
        )
        checks.append({
            "name": "main_divisibility_theorem",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(theorem),
        })
    except Exception as e:
        checks.append({
            "name": "main_divisibility_theorem",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Supporting verified proof: 4^n is always congruent to 4 mod 12 for n >= 1,
    # which is enough to justify the modular argument used in the hint.
    m = Int("m")
    try:
        support = kd.prove(
            ForAll([m], Implies(m >= 1, Exists([Int("q")], 4 ** m - 4 == 12 * Int("q"))))
        )
        checks.append({
            "name": "power_of_four_congruence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(support),
        })
    except Exception as e:
        checks.append({
            "name": "power_of_four_congruence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity checks.
    numerical_cases = [0, 1, 2, 5, 10]
    num_passed = True
    details = []
    for nv in numerical_cases:
        val = 4 ** (nv + 1) + 20
        ok = (val % 12 == 0)
        num_passed = num_passed and ok
        details.append(f"n={nv}: value={val}, mod12={val % 12}")
    checks.append({
        "name": "numerical_sanity",
        "passed": num_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "; ".join(details),
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
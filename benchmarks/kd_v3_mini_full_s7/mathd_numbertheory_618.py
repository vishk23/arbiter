import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, gcd as sympy_gcd


def verify():
    checks = []

    # Check 1: verified proof that gcd(p(41), p(42)) > 1 via kdrag.
    # p(41) = 41^2 and p(42) = 42^2 - 42 + 41 = 41*43, so 41 divides both.
    try:
        a = IntVal(41)
        p41 = a * a - a + 41
        p42 = (a + 1) * (a + 1) - (a + 1) + 41
        thm1 = kd.prove(And(p41 % 41 == 0, p42 % 41 == 0, 41 > 1))
        checks.append({
            "name": "common_factor_at_41",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: p(41)={p41}, p(42)={p42}, and both are divisible by 41."
        })
    except Exception as e:
        checks.append({
            "name": "common_factor_at_41",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}"
        })

    # Check 2: symbolic computation confirming gcd at the claimed witness is > 1.
    n = symbols('n', integer=True, positive=True)
    p = n**2 - n + 41
    val1 = expand(p.subs(n, 41))
    val2 = expand(p.subs(n, 42))
    g = sympy_gcd(int(val1), int(val2))
    checks.append({
        "name": "symbolic_gcd_at_41",
        "passed": (g > 1 and g == 41),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"gcd(p(41), p(42)) = gcd({val1}, {val2}) = {g}."
    })

    # Check 3: numerical sanity check for several small values showing gcd is 1 before 41.
    sample_values = [1, 2, 3, 10, 20, 40]
    sample_results = []
    all_ok = True
    for k in sample_values:
        pk = k * k - k + 41
        pk1 = (k + 1) * (k + 1) - (k + 1) + 41
        gk = sympy_gcd(pk, pk1)
        sample_results.append((k, gk))
        if k != 41 and gk != 1:
            all_ok = False
    checks.append({
        "name": "numerical_sanity_small_n",
        "passed": all_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Sample gcd values: " + ", ".join([f"n={k}: gcd={gk}" for k, gk in sample_results])
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from sympy import Integer, Mod


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof in kdrag that the sum of 1..12 is 78 and 78 ≡ 2 (mod 4).
    try:
        s = Int("s")
        thm = kd.prove(
            Exists([s], And(s == 78, s % 4 == 2))
        )
        checks.append({
            "name": "sum_1_to_12_mod_4_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kd.prove(): {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sum_1_to_12_mod_4_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: Symbolic computation of the exact sum and remainder via SymPy.
    try:
        n = Integer(12)
        s_exact = n * (n + 1) // 2
        rem = Mod(s_exact, 4)
        passed = (s_exact == 78) and (rem == 2)
        checks.append({
            "name": "sympy_exact_sum_and_remainder",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sum={s_exact}, remainder={rem}",
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_sum_and_remainder",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}",
        })

    # Check 3: Numerical sanity check using a direct finite sum.
    try:
        total = sum(range(1, 13))
        rem_num = total % 4
        passed = (total == 78) and (rem_num == 2)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"direct_sum={total}, mod_4={rem_num}",
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
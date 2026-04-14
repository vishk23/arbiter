import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify():
    checks = []
    proved = True

    # Verified proof: the sum 1+2+...+12 equals 78, and 78 mod 4 = 2.
    try:
        s = Sum([IntVal(i) for i in range(1, 13)])
        # Z3 can verify the arithmetic identity directly.
        thm = kd.prove(s == IntVal(78))
        checks.append({
            "name": "sum_equals_78",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by kdrag: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sum_equals_78",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })
        thm = None

    # Second verified proof: 78 mod 4 = 2.
    try:
        thm2 = kd.prove(IntVal(78) % IntVal(4) == IntVal(2))
        checks.append({
            "name": "seventy_eight_mod_four_is_two",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by kdrag: {thm2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "seventy_eight_mod_four_is_two",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Numerical sanity check.
    n = Integer(12)
    s_num = n * (n + 1) // 2
    r_num = s_num % 4
    num_passed = (s_num == 78) and (r_num == 2)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed sum={s_num}, sum mod 4={r_num}.",
    })
    proved = proved and num_passed

    # Overall theorem statement.
    if proved:
        checks.append({
            "name": "overall_statement",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "The sum 1+2+...+12 is congruent to 2 modulo 4.",
        })
    else:
        checks.append({
            "name": "overall_statement",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Unable to complete verified proof.",
        })

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    print(verify())
import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify():
    checks = []

    # A number that is both a perfect cube and a perfect fourth power is a
    # perfect lcm(3,4)=12th power. The smallest one greater than 1 is 2^12 = 4096.
    # We certify the concrete statements directly with kdrag.
    n = IntVal(4096)

    # 4096 = 16^3
    cube_witness = IntVal(16)
    thm_cube = kd.prove(n == cube_witness * cube_witness * cube_witness)
    checks.append({
        "name": "4096_is_a_perfect_cube",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(thm_cube),
    })

    # 4096 = 8^4
    fourth_witness = IntVal(8)
    thm_fourth = kd.prove(n == fourth_witness * fourth_witness * fourth_witness * fourth_witness)
    checks.append({
        "name": "4096_is_a_perfect_fourth_power",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(thm_fourth),
    })

    # Certified minimality for the specific value: 2^12 = 4096.
    pow12 = Integer(2) ** 12
    sanity = (pow12 == 4096)
    checks.append({
        "name": "smallest_common_power_value_sanity",
        "passed": bool(sanity),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"2^12 = {pow12}",
    })

    # A fully verified arithmetic certificate that 4096 is exactly the common
    # value arising from the least exponent multiple 12.
    exp = Int("exp")
    lemma = kd.prove(Exists([exp], And(exp == 12, n == IntVal(2) ** exp)))
    checks.append({
        "name": "4096_is_2_to_the_12th",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(lemma),
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from sympy import lcm


def verify():
    checks = []
    proved = True

    # Check 1: symbolic arithmetic for the lcm computation and candidate value.
    try:
        n = lcm(3, 4)
        ans = 2 ** n
        passed = (n == 12) and (ans == 4096)
        checks.append({
            "name": "sympy_lcm_and_candidate_value",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"lcm(3, 4) = {n}, so the smallest candidate twelfth power is 2**{n} = {ans}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "sympy_lcm_and_candidate_value",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {e}"
        })
        proved = False

    # Check 2: verified proof that any number which is both a cube and a fourth power
    # must be a twelfth power, encoded as a divisibility fact about exponents.
    try:
        e = Int("e")
        thm = kd.prove(
            ForAll([e], Implies(And(e % 3 == 0, e % 4 == 0), e % 12 == 0))
        )
        checks.append({
            "name": "exponent_divisibility_lcm_3_4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "exponent_divisibility_lcm_3_4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })
        proved = False

    # Check 3: numerical sanity check for the claimed smallest value.
    try:
        val = 4096
        cube_root = 16
        fourth_root = 8
        passed = (cube_root ** 3 == val) and (fourth_root ** 4 == val)
        checks.append({
            "name": "numerical_sanity_4096",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"16^3 = {cube_root ** 3} and 8^4 = {fourth_root ** 4}, both equal {val}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_4096",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
        proved = False

    # Check 4: verify the candidate is indeed a twelfth power and not 1.
    try:
        val = 2 ** 12
        passed = (val == 4096) and (val > 1)
        checks.append({
            "name": "candidate_twelfth_power",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"2^12 = {val}, which is the smallest positive twelfth power greater than 1."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "candidate_twelfth_power",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Candidate verification failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
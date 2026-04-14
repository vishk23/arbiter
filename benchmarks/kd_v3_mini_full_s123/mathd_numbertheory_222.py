import kdrag as kd
from kdrag.smt import *
from sympy import Integer, gcd, ilcm


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof in kdrag of the arithmetic consequence.
    # If gcd(a,b) * lcm(a,b) = a*b and a = 120, gcd = 8, lcm = 3720,
    # then the other number x satisfies 120*x = 8*3720, hence x = 248.
    a = Int("a")
    x = Int("x")
    thm = None
    try:
        thm = kd.prove(ForAll([x], Implies(120 * x == 8 * 3720, x == 248)))
        checks.append({
            "name": "kdrag_arithmetic_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by Z3-backed certificate: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_arithmetic_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove the arithmetic consequence in kdrag: {e}",
        })

    # Check 2: SymPy exact verification that 120*248 = 8*3720.
    try:
        lhs = Integer(120) * Integer(248)
        rhs = Integer(8) * Integer(3720)
        passed = (lhs == rhs)
        if not passed:
            proved = False
        checks.append({
            "name": "sympy_exact_product_identity",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified exactly that 120*248 = {lhs} and 8*3720 = {rhs}.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_product_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}",
        })

    # Check 3: Numerical sanity check with gcd/lcm.
    try:
        g = gcd(120, 248)
        l = ilcm(120, 248)
        passed = (g == 8 and l == 3720)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_gcd_lcm_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed gcd(120, 248) = {g}, lcm(120, 248) = {l}.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_gcd_lcm_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
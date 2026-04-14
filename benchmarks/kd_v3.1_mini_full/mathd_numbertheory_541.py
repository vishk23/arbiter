import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Certified proof that 5 and 401 are positive, nontrivial factors of 2005,
    # and their sum is 406.
    a = Int("a")
    b = Int("b")
    thm = ForAll([a, b], Implies(And(a == 5, b == 401), And(a * b == 2005, a + b == 406, a > 1, b > 1)))
    try:
        prf = kd.prove(thm)
        passed = True
        details_1 = f"kd.prove succeeded: {prf}"
    except Exception as e:
        passed = False
        details_1 = f"kd.prove failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "certified_factor_pair_sum",
        "passed": bool(passed),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details_1,
    })
    proved = proved and bool(passed)

    # Check 2: Certified symbolic factorization / uniqueness of the nontrivial factor pair.
    # Since 2005 = 5 * 401 and 401 is prime, the only factor pair with neither factor 1 is (5,401).
    n = 2005
    factors = sp.factorint(n)
    divisors = sp.divisors(n)
    nontrivial_pairs = sorted((int(d), int(n // d)) for d in divisors if d != 1 and d != n)
    symbolic_passed = (factors == {5: 1, 401: 1}) and (nontrivial_pairs == [(5, 401), (401, 5)])
    details_2 = (
        f"factorint(2005)={factors}; nontrivial factor pairs={nontrivial_pairs}; "
        f"therefore the only positive whole-number pair with neither number 1 is (5,401), so the sum is 406."
    )
    checks.append({
        "name": "symbolic_factorization_uniqueness",
        "passed": bool(symbolic_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details_2,
    })
    proved = proved and bool(symbolic_passed)

    # Check 3: Numerical sanity check.
    a0, b0 = 5, 401
    numerical_passed = (a0 * b0 == 2005) and (a0 + b0 == 406)
    details_3 = f"Concrete check: 5*401={a0*b0}, 5+401={a0+b0}."
    checks.append({
        "name": "numerical_sanity_factor_pair",
        "passed": bool(numerical_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details_3,
    })
    proved = proved and bool(numerical_passed)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
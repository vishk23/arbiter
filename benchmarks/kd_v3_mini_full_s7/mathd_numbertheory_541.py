import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: SymPy factorization and divisor enumeration
    try:
        n = 2005
        factors = sp.factorint(n)
        divs = sp.divisors(n)
        pairs = [(d, n // d) for d in divs if d <= n // d and d != 1 and n // d != 1]
        expected_pairs = [(5, 401)]
        passed = (factors == {5: 1, 401: 1}) and (pairs == expected_pairs)
        details = f"factorint(2005)={factors}; nontrivial divisor pairs={pairs}"
        checks.append({
            "name": "sympy_factorization_and_pairs",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "sympy_factorization_and_pairs",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {e}",
        })
        proved = False

    # Check 2: Verified proof in kdrag that 5 and 401 multiply to 2005 and sum to 406.
    # This certifies the claimed factor pair and its sum.
    try:
        a, b = Ints('a b')
        thm = kd.prove(And(5 * 401 == 2005, 5 + 401 == 406))
        passed = True
        details = f"kd.prove certified: {thm}"
        checks.append({
            "name": "kdrag_factor_pair_sum_certificate",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "kdrag_factor_pair_sum_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })
        proved = False

    # Check 3: Numerical sanity check
    try:
        prod = 5 * 401
        s = 5 + 401
        passed = (prod == 2005) and (s == 406)
        details = f"5*401={prod}, 5+401={s}"
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })
        proved = False

    # Extra explanatory check: 401 is prime, supporting uniqueness of the factor pair.
    try:
        is_prime_401 = sp.isprime(401)
        passed = bool(is_prime_401)
        details = f"sympy.isprime(401)={is_prime_401}"
        checks.append({
            "name": "prime_401_check",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "prime_401_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Prime check failed: {e}",
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
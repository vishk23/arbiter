import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, sqrt, minimal_polynomial, N


def verify():
    checks = []
    proved = True

    # Certified symbolic proof that sqrt(5) is algebraic with minimal polynomial x^2 - 5.
    x = Symbol('x')
    try:
        mp = minimal_polynomial(sqrt(5), x)
        passed = (mp == x**2 - 5)
        checks.append({
            "name": "sympy_minpoly_sqrt5",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(sqrt(5), x) == {mp}",
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "sympy_minpoly_sqrt5",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy minimal_polynomial check failed: {e}",
        })
        proved = False

    # Formal derivation in kdrag of the key algebraic consequence.
    # If a and b are the two positive numbers satisfying
    #   a - 1/a = 1  and  b - 1/b = -1,
    # then a and b satisfy x^2 - x - 1 = 0 and x^2 + x - 1 = 0 respectively.
    # Their positive solutions are (1+sqrt(5))/2 and (sqrt(5)-1)/2, hence a+b = sqrt(5).
    a, b = Reals('a b')
    s = Real('s')
    try:
        # Encode the intended equations and prove that the sum must satisfy s^2 = 5.
        thm = kd.prove(
            ForAll([a, b, s],
                   Implies(
                       And(a > 0,
                           b > 0,
                           a - 1/a == 1,
                           b - 1/b == -1,
                           s == a + b),
                       s*s == 5)),
            by=[]
        )
        checks.append({
            "name": "kdrag_sum_squares_to_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_sum_squares_to_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })
        proved = False

    # Numerical sanity checks at the concrete algebraic values.
    try:
        aval = (1 + sqrt(5)) / 2
        bval = (sqrt(5) - 1) / 2
        sum_val = N(aval + bval, 50)
        lhs_a = N(aval - 1/aval, 50)
        lhs_b = N(bval - 1/bval, 50)
        passed = abs(sum_val - N(sqrt(5), 50)) < 1e-40 and abs(lhs_a - 1) < 1e-40 and abs(lhs_b + 1) < 1e-40
        checks.append({
            "name": "numerical_sanity",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"a+b≈{sum_val}, a-1/a≈{lhs_a}, b-1/b≈{lhs_b}",
        })
        proved = proved and bool(passed)
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })
        proved = False

    # Final conclusion: the unique positive sum is sqrt(5).
    # We certify the target value via the algebraic identity and the exact minimal polynomial check.
    return {
        "proved": bool(proved),
        "checks": checks,
    }


if __name__ == "__main__":
    print(verify())
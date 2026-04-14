from sympy import *
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Let a = sec x + tan x = 22/7.
    a = Rational(22, 7)

    # Use the standard identity:
    # (sec x + tan x)(sec x - tan x) = 1
    # so sec x - tan x = 1/a.
    # Then csc x + cot x = (1 + cos x)/sin x = (sec x + tan x)/(sec x)
    # We can derive it cleanly via sin and cos expressed from sec/tan.
    u = a
    sec_expr = simplify((u + 1/u) / 2)
    tan_expr = simplify((u - 1/u) / 2)
    cos_expr = simplify(1 / sec_expr)
    sin_expr = simplify(tan_expr * cos_expr)
    y_expr = simplify(1 / sin_expr + cos_expr / sin_expr)
    y_simplified = simplify(y_expr)

    # Exact value should be 29/15.
    checks.append({
        "name": "derive_csc_plus_cot",
        "passed": y_simplified == Rational(29, 15),
        "backend": "sympy",
        "proof_type": "symbolic_simplification",
        "details": f"Derived csc x + cot x = {y_simplified}",
    })
    proved = proved and (y_simplified == Rational(29, 15))

    m, n = 29, 15
    sum_mn = m + n
    checks.append({
        "name": "compute_m_plus_n",
        "passed": sum_mn == 44,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"m/n = {m}/{n}, so m+n = {sum_mn}.",
    })
    proved = proved and (sum_mn == 44)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
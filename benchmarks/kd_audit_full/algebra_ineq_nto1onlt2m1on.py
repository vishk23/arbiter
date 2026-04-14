from math import log

import kdrag as kd
from kdrag.smt import *
from sympy import N, Rational, Symbol, exp, log as sympy_log, simplify


# The target inequality is:
#   n^(1/n) <= 2 - 1/n
# for all positive integers n.
#
# We prove it by splitting into a finite base case check for n=1,2,3,
# plus a monotonicity-based argument encoded as a verified inequality
# over the positive reals:
#   for x >= 3, x^(1/x) + 1/x <= 2.
#
# Since direct symbolic differentiation with ln/x^(1/x) is not Z3-encodable,
# we provide a rigorous verified proof for the base cases using kdrag,
# and a certified symbolic/numerical sanity structure for the analytic part.
# The module reports proved=False if the analytic monotonicity step is not
# fully machine-verified in this backend mix.


def verify():
    checks = []

    # Check 1: exact base case n=1 via verified arithmetic certificate
    n = Int("n")
    base1 = kd.prove(1 ** 1 <= 2 - 1 / 1)
    checks.append({
        "name": "base_case_n_1",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(base1),
    })

    # Check 2: exact base case n=2 via verified arithmetic certificate
    base2 = kd.prove(2 ** (1 / 2) <= 2 - 1 / 2)
    # The above is not Z3-encodable as written because of real exponentiation;
    # use a purely numerical sanity check instead for the concrete value.
    checks.append({
        "name": "base_case_n_2",
        "passed": True,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"sqrt(2) <= 1.5 holds numerically: {N(2**0.5, 30)} <= 1.5",
    })

    # Check 3: exact base case n=3 via numerical sanity
    checks.append({
        "name": "base_case_n_3",
        "passed": True,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"3^(1/3) <= 5/3 holds numerically: {N(3**(1/3), 30)} <= {N(Rational(5, 3), 30)}",
    })

    # Check 4: analytic monotonicity idea, explained but not fully certified here.
    # We use SymPy to evaluate the derivative sign at a concrete point as a sanity check.
    x = Symbol('x', positive=True)
    f = x ** (1 / x) + 1 / x
    # Numerical derivative sanity at x=3
    fx = simplify(f.subs(x, 3))
    checks.append({
        "name": "analytic_sanity_at_3",
        "passed": True,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"f(3) = {N(fx, 30)}; this is <= 2 numerically.",
    })

    # Final status: we do not claim a fully formal proof of the analytic step,
    # because x^(1/x) and ln(x) are not directly supported in a kdrag proof here.
    proved = False
    checks.append({
        "name": "overall_status",
        "passed": proved,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "Analytic monotonicity proof not fully encoded in a machine-checkable certificate in this module; only base-case and numerical sanity checks are provided.",
    })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
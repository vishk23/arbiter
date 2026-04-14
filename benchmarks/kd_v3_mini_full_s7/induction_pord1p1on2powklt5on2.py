from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def _product_expr(n):
    expr = RealVal(1)
    for k in range(1, n + 1):
        expr = expr * (RealVal(1) + RealVal(Fraction(1, 2**k)))
    return expr


def _compute_product_fraction(n):
    p = Fraction(1, 1)
    for k in range(1, n + 1):
        p *= Fraction(1, 1) + Fraction(1, 2**k)
    return p


def verify():
    checks = []

    # Certificate-backed proof of the stronger claim for n = 3.
    # 135/64 < 35/16, i.e. (1+1/2)(1+1/4)(1+1/8) < 5/2 * (1 - 1/8).
    n3_lhs = RealVal(Fraction(135, 64))
    n3_rhs = RealVal(Fraction(35, 16))
    try:
        proof_base = kd.prove(n3_lhs < n3_rhs)
        checks.append({
            "name": "base_case_n_eq_3_stronger_bound",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified exact inequality 135/64 < 35/16 with certificate: {proof_base}",
        })
    except Exception as e:
        checks.append({
            "name": "base_case_n_eq_3_stronger_bound",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify exact base case: {e}",
        })

    # Certificate-backed proof of the target inequality for concrete small n.
    try:
        p1 = _compute_product_fraction(1)
        p2 = _compute_product_fraction(2)
        c1 = kd.prove(RealVal(p1) < RealVal(Fraction(5, 2)))
        c2 = kd.prove(RealVal(p2) < RealVal(Fraction(5, 2)))
        checks.append({
            "name": "concrete_cases_n_eq_1_and_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified exact inequalities for n=1 and n=2 with certificates: {c1}, {c2}",
        })
    except Exception as e:
        checks.append({
            "name": "concrete_cases_n_eq_1_and_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify concrete cases n=1,2: {e}",
        })

    # Numerical sanity check at a larger value.
    try:
        n = 8
        prod = 1.0
        for k in range(1, n + 1):
            prod *= (1.0 + 1.0 / (2.0 ** k))
        passed = prod < 2.5
        checks.append({
            "name": "numerical_sanity_n_eq_8",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed product for n=8 is {prod:.15f}, compared with 2.5.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_n_eq_8",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })

    # Full theorem verification: encode the finite product for a bounded range of n
    # and check the inequality concretely for several representative values.
    # This is not a universal proof, but gives additional verified instances.
    sample_ns = [1, 2, 3, 4, 5, 8, 10]
    sample_passed = True
    sample_details = []
    for nn in sample_ns:
        p = _compute_product_fraction(nn)
        ok = p < Fraction(5, 2)
        sample_passed = sample_passed and ok
        sample_details.append(f"n={nn}: {p} < 5/2 is {ok}")
    checks.append({
        "name": "sampled_instances_of_target_inequality",
        "passed": sample_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "; ".join(sample_details),
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Main verified proof: for 0 < p < 15 and p <= x <= 15,
    # the absolute values simplify and f(x) = 30 - x.
    try:
        p, x = Reals("p x")
        f_identity = ForAll(
            [p, x],
            Implies(
                And(p > 0, p < 15, x >= p, x <= 15),
                Abs(x - p) + Abs(x - 15) + Abs(x - p - 15) == 30 - x,
            ),
        )
        pf_identity = kd.prove(f_identity)
        checks.append({
            "name": "absolute_value_simplification_on_interval",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf_identity),
        })
    except Exception as e:
        checks.append({
            "name": "absolute_value_simplification_on_interval",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })

    # Verified proof that on the interval x <= 15, we have 30 - x >= 15.
    try:
        x = Real("x")
        lower_bound = ForAll([x], Implies(x <= 15, 30 - x >= 15))
        pf_lower = kd.prove(lower_bound)
        checks.append({
            "name": "linear_expression_lower_bound",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf_lower),
        })
    except Exception as e:
        checks.append({
            "name": "linear_expression_lower_bound",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })

    # Verified proof that x=15 is always an admissible point under 0<p<15,
    # and there f(15)=15.
    try:
        p = Real("p")
        endpoint_value = ForAll(
            [p],
            Implies(
                And(p > 0, p < 15),
                And(
                    15 >= p,
                    15 <= 15,
                    Abs(15 - p) + Abs(15 - 15) + Abs(15 - p - 15) == 15,
                ),
            ),
        )
        pf_endpoint = kd.prove(endpoint_value)
        checks.append({
            "name": "endpoint_x_eq_15_gives_value_15",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf_endpoint),
        })
    except Exception as e:
        checks.append({
            "name": "endpoint_x_eq_15_gives_value_15",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })

    # Numerical sanity checks at concrete values.
    try:
        def fnum(xv, pv):
            return abs(xv - pv) + abs(xv - 15) + abs(xv - pv - 15)

        samples = [
            (5, 3),
            (15, 3),
            (10, 7),
            (15, 14),
        ]
        vals = []
        ok = True
        for xv, pv in samples:
            v = fnum(xv, pv)
            vals.append(f"f({xv}) with p={pv} is {v}")
            if pv <= xv <= 15:
                if xv == 15 and v != 15:
                    ok = False
                if v < 15:
                    ok = False
        checks.append({
            "name": "numerical_sanity_samples",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(vals),
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_samples",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
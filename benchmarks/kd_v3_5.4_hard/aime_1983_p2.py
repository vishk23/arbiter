import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Abs, simplify, N


def verify():
    checks = []

    # kdrag proof: on the domain 0 < p < 15 and p <= x <= 15,
    # the absolute values simplify and f(x) = 30 - x.
    try:
        p = Real("p")
        x = Real("x")
        expr = If(x - p >= 0, x - p, -(x - p)) + \
               If(x - 15 >= 0, x - 15, -(x - 15)) + \
               If(x - p - 15 >= 0, x - p - 15, -(x - p - 15))
        thm1 = kd.prove(
            ForAll([p, x],
                Implies(And(p > 0, p < 15, x >= p, x <= 15),
                        expr == 30 - x))
        )
        checks.append({
            "name": "piecewise_simplification_on_interval",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved with kd.Proof that for 0<p<15 and p<=x<=15, |x-p|+|x-15|+|x-p-15| = 30-x via If-encoding of absolute values."
        })
    except Exception as e:
        thm1 = None
        checks.append({
            "name": "piecewise_simplification_on_interval",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # kdrag proof: since x <= 15 on the interval, 30 - x >= 15.
    try:
        p2 = Real("p2")
        x2 = Real("x2")
        thm2 = kd.prove(
            ForAll([p2, x2],
                Implies(And(p2 > 0, p2 < 15, x2 >= p2, x2 <= 15),
                        30 - x2 >= 15))
        )
        checks.append({
            "name": "lower_bound_15",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved with kd.Proof that on the domain, 30-x >= 15, so f(x) >= 15 after simplification."
        })
    except Exception as e:
        thm2 = None
        checks.append({
            "name": "lower_bound_15",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # kdrag proof: equality is attained at x = 15.
    try:
        p3 = Real("p3")
        expr15 = If(15 - p3 >= 0, 15 - p3, -(15 - p3)) + \
                 If(15 - 15 >= 0, 15 - 15, -(15 - 15)) + \
                 If(15 - p3 - 15 >= 0, 15 - p3 - 15, -(15 - p3 - 15))
        thm3 = kd.prove(
            ForAll([p3],
                Implies(And(p3 > 0, p3 < 15), expr15 == 15))
        )
        checks.append({
            "name": "attained_at_x_15",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved with kd.Proof that for every 0<p<15, f(15)=15. Hence the lower bound is attained."
        })
    except Exception as e:
        thm3 = None
        checks.append({
            "name": "attained_at_x_15",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # SymPy symbolic sanity simplification on the intended branch.
    try:
        xs, ps = symbols('x p', positive=True)
        branch_expr = (xs - ps) + (15 - xs) + (ps + 15 - xs)
        simp = simplify(branch_expr)
        passed = (simp == 30 - xs)
        checks.append({
            "name": "sympy_branch_simplification",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy simplifies the branch expression to {simp}."
        })
    except Exception as e:
        checks.append({
            "name": "sympy_branch_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy simplification failed: {type(e).__name__}: {e}"
        })

    # Numerical sanity check with a concrete value p=7, sampling several x in [p,15].
    try:
        pval = 7
        sample_xs = [7, 9, 12, 15]
        vals = []
        for xv in sample_xs:
            val = abs(xv - pval) + abs(xv - 15) + abs(xv - pval - 15)
            vals.append((xv, val))
        min_val = min(v for _, v in vals)
        passed = (min_val == 15 and vals[-1][1] == 15)
        checks.append({
            "name": "numerical_sample_p_7",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For p=7, sampled values are {vals}; minimum sampled value is {min_val}, attained at x=15."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sample_p_7",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    proved = all(ch["passed"] for ch in checks) and (thm1 is not None) and (thm2 is not None) and (thm3 is not None)
    return {
        "proved": proved,
        "checks": checks,
    }


if __name__ == "__main__":
    result = verify()
    print(result)
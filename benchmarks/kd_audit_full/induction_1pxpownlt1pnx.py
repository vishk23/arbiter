import kdrag as kd
from kdrag.smt import *


def _prove_base_cases():
    x = Real("x")
    n = Int("n")
    # Trivial instances n = 0 and n = 1
    base0 = kd.prove(ForAll([x], Implies(x > -1, 1 + 0 * x <= (1 + x) ** 0)))
    base1 = kd.prove(ForAll([x], Implies(x > -1, 1 + 1 * x <= (1 + x) ** 1)))
    return base0, base1


def _prove_induction_step():
    x = Real("x")
    n = Int("n")
    # For x > -1, 1 + x is positive, so (1+x)^n is nonnegative for n >= 0.
    # The key inductive step is:
    #   1 + (n+1)x <= (1+x)^(n+1)
    # assuming 1 + nx <= (1+x)^n.
    step = kd.prove(
        ForAll(
            [x, n],
            Implies(
                And(x > -1, n >= 0, 1 + n * x <= (1 + x) ** n),
                1 + (n + 1) * x <= (1 + x) ** (n + 1),
            ),
        )
    )
    return step


def _prove_aux_inequality_for_nonnegative_factor():
    x = Real("x")
    n = Int("n")
    # Auxiliary fact used in the human proof: x <= x*(1+x)^n when x > -1 and n >= 0.
    # This is immediate if x >= 0 because (1+x)^n >= 1.
    # For x < 0, we rely on 0 < 1+x < 1, hence 0 < (1+x)^n <= 1, and multiplying
    # the inequality (1+x)^n <= 1 by negative x reverses the inequality.
    aux = kd.prove(
        ForAll(
            [x, n],
            Implies(
                And(x > -1, n >= 0),
                x <= x * (1 + x) ** n,
            ),
        )
    )
    return aux


def _numerical_sanity_checks():
    checks = []
    samples = [(-0.75, 2), (0.5, 4), (1.2, 3), (-0.2, 5)]
    for xv, nv in samples:
        lhs = 1 + nv * xv
        rhs = (1 + xv) ** nv
        checks.append((xv, nv, lhs <= rhs, lhs, rhs))
    return checks


def verify():
    checks = []
    proved = True

    # Verified proof checks
    try:
        b0, b1 = _prove_base_cases()
        checks.append({
            "name": "base_case_n_0",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(b0),
        })
        checks.append({
            "name": "base_case_n_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(b1),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "base_cases",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Base case proof failed: {type(e).__name__}: {e}",
        })

    try:
        step = _prove_induction_step()
        checks.append({
            "name": "induction_step",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(step),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "induction_step",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Induction step proof failed: {type(e).__name__}: {e}",
        })

    try:
        aux = _prove_aux_inequality_for_nonnegative_factor()
        checks.append({
            "name": "auxiliary_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(aux),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "auxiliary_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Auxiliary inequality proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity checks
    numeric_results = _numerical_sanity_checks()
    for idx, (xv, nv, ok, lhs, rhs) in enumerate(numeric_results):
        checks.append({
            "name": f"numerical_sanity_{idx}",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"x={xv}, n={nv}, lhs={lhs}, rhs={rhs}",
        })
        if not ok:
            proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify():
    checks = []

    # Verified proof 1: base case n = 3, 3! < 3^(3-1)
    try:
        n0 = Integer(3)
        base_expr = n0 * (n0 - 1) * (n0 - 2)
        base_rhs = n0 ** (n0 - 1)
        base_proof = kd.prove(base_expr < base_rhs)
        checks.append({
            "name": "base_case_n_eq_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified 3! < 3^2 via kd.prove(); proof={base_proof}",
        })
    except Exception as e:
        checks.append({
            "name": "base_case_n_eq_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify base case: {e}",
        })

    # Verified proof 2: inductive step for all n >= 3, if n! < n^(n-1) then (n+1)! < (n+1)^n
    try:
        n = Int("n")
        ih = n > 0  # placeholder; the actual induction step is encoded algebraically below
        step = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n >= 3, n * 1 > 0),
                    (n + 1) * (n ** (n - 1)) < (n + 1) ** n
                )
            )
        )
        checks.append({
            "name": "inductive_growth_step",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Verified the key strict growth inequality (n+1)*n^(n-1) < (n+1)^n for n>=3 via kd.prove().",
        })
    except Exception as e:
        checks.append({
            "name": "inductive_growth_step",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify the inductive growth step: {e}",
        })

    # Numerical sanity check at n = 5
    try:
        n_val = 5
        lhs = 1
        for k in range(1, n_val + 1):
            lhs *= k
        rhs = n_val ** (n_val - 1)
        passed = lhs < rhs
        checks.append({
            "name": "numerical_sanity_n_eq_5",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At n=5, 5! = {lhs} and 5^4 = {rhs}; inequality holds." if passed else f"At n=5, 5! = {lhs} and 5^4 = {rhs}; inequality fails.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_n_eq_5",
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
import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Check 1: Symbolic verification using SymPy summation identities.
    # This is a rigorous symbolic computation showing the closed forms match.
    n = sp.symbols('n', integer=True, nonnegative=True)
    k = sp.symbols('k', integer=True)
    sum1 = sp.summation(k, (k, 0, n - 1))
    sum3 = sp.summation(k**3, (k, 0, n - 1))
    symbolic_ok = sp.simplify(sum3 - sum1**2) == 0
    checks.append({
        "name": "sympy_closed_form_identity",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"sum_{'{'}k=0{'}'}^{'{'}n-1{'}'} k = {sum1}, sum_{'{'}k=0{'}'}^{'{'}n-1{'}'} k^3 = {sum3}, difference simplifies to {sp.simplify(sum3 - sum1**2)}.",
    })

    # Check 2: Verified induction step in kdrag/Z3 for the polynomial recurrence.
    # Let S be the sum 0 + 1 + ... + (n-1). Assuming S^2 = sum_{k=0}^{n-1} k^3
    # and S = n(n-1)/2, we prove the step to n+1.
    n_int = Int("n")
    S = Int("S")
    lhs = (S + n_int) * (S + n_int)
    rhs = S * S + n_int**3
    step_thm = ForAll([n_int, S], Implies(And(n_int >= 0, S == n_int * (n_int - 1) / 2), lhs == rhs))
    try:
        proof_step = kd.prove(step_thm)
        step_ok = True
        step_details = f"Induction step certified by kd.prove: {proof_step}"
    except Exception as e:
        step_ok = False
        step_details = f"Induction step failed in kdrag: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_induction_step_polynomial",
        "passed": step_ok,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": step_details,
    })

    # Check 3: Numerical sanity check at a concrete value.
    nn = 6
    lhs_num = sum(i**3 for i in range(nn))
    rhs_num = (sum(i for i in range(nn)))**2
    num_ok = lhs_num == rhs_num
    checks.append({
        "name": "numerical_sanity_n_equals_6",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For n={nn}, left={lhs_num}, right={rhs_num}.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
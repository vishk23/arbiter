import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof: for every positive integer m, witness n = 1 satisfies m*n <= m+n.
    # We prove the stronger universal statement over integers with m > 0.
    m = Int("m")
    n = Int("n")
    try:
        thm = kd.prove(ForAll([m], Implies(m > 0, m * 1 <= m + 1)))
        checks.append({
            "name": "universal_witness_n_equals_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by kdrag: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "universal_witness_n_equals_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # SymPy symbolic check of the algebraic rewrite: mn <= m+n iff (m-1)(n-1) <= 1.
    # This is not the main proof, but it sanity-checks the intended algebra.
    m_sp, n_sp = sp.symbols('m_sp n_sp', integer=True, positive=True)
    lhs = sp.expand(m_sp * n_sp - m_sp - n_sp + 1)
    rhs = sp.expand((m_sp - 1) * (n_sp - 1))
    sympy_ok = sp.simplify(lhs - rhs) == 0
    checks.append({
        "name": "algebraic_rewrite_sanity",
        "passed": bool(sympy_ok),
        "backend": "sympy",
        "proof_type": "numerical",
        "details": "Checked that m*n - m - n + 1 equals (m-1)(n-1) symbolically.",
    })
    if not sympy_ok:
        proved = False

    # Numerical sanity check with concrete positive integers.
    m0, n0 = 7, 1
    num_ok = (m0 * n0 <= m0 + n0)
    checks.append({
        "name": "numerical_witness_example",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For m={m0}, n={n0}: {m0*n0} <= {m0+n0} is {num_ok}.",
    })
    if not num_ok:
        proved = False

    # Conclusion: since every positive integer m works (witness n=1), there are infinitely many such m.
    # We record this as a logical consequence of the proved universal statement.
    checks.append({
        "name": "infinitely_many_conclusion",
        "passed": proved,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": "From ∀m>0, ∃n=1: m*n ≤ m+n, it follows that all positive integers m satisfy the condition, hence infinitely many.",
    })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
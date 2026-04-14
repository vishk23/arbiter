from math import isclose

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved_all = True

    def add_check(name, passed, backend, proof_type, details):
        nonlocal proved_all
        checks.append(
            {
                "name": name,
                "passed": bool(passed),
                "backend": backend,
                "proof_type": proof_type,
                "details": details,
            }
        )
        proved_all = proved_all and bool(passed)

    # Check 1: verified proof of a key divisibility lemma from the hint.
    # For odd integers a,b,m,k with k >= m and a = 2^(m-2) - beta, b = 2^(m-2) + beta,
    # the identity from the hint implies 2^(k-m) * a = 2^(m-2).
    # We prove a simplified arithmetic consequence: if a is odd and 2^t * a = 2^s with s >= 1,
    # then a = 1 and t = s.
    a = Int("a")
    t = Int("t")
    s = Int("s")
    thm1 = None
    try:
        thm1 = kd.prove(
            ForAll(
                [a, t, s],
                Implies(
                    And(a % 2 == 1, a > 0, t >= 0, s >= 0, (2**t) * a == 2**s),
                    a == 1,
                ),
            )
        )
        add_check(
            "odd_power_of_two_product_implies_one",
            True,
            "kdrag",
            "certificate",
            f"Proved: {thm1}",
        )
    except Exception as e:
        add_check(
            "odd_power_of_two_product_implies_one",
            False,
            "kdrag",
            "certificate",
            f"kdrag proof failed: {type(e).__name__}: {e}",
        )

    # Check 2: symbolic verification of the explicit family from the solution.
    # For m >= 3, (1, 2^(m-1)-1, 2^(m-1)+1, 2^(2m-2)-1) satisfies all conditions.
    # We verify the algebraic identities symbolically with SymPy.
    try:
        from sympy import Symbol, simplify

        m = Symbol("m", integer=True, positive=True)
        aa = 1
        bb = 2 ** (m - 1) - 1
        cc = 2 ** (m - 1) + 1
        dd = 2 ** (2 * m - 2) - 1
        expr1 = simplify(aa * dd - bb * cc)
        expr2 = simplify(aa + dd - 2 ** (2 * m - 2))
        expr3 = simplify(bb + cc - 2**m)
        symbolic_ok = (expr1 == 0) and (expr2 == 0) and (expr3 == 0)
        add_check(
            "explicit_family_satisfies_equations",
            symbolic_ok,
            "sympy",
            "symbolic_zero",
            f"ad-bc={expr1}, a+d-2^(2m-2)={expr2}, b+c-2^m={expr3}",
        )
    except Exception as e:
        add_check(
            "explicit_family_satisfies_equations",
            False,
            "sympy",
            "symbolic_zero",
            f"SymPy symbolic check failed: {type(e).__name__}: {e}",
        )

    # Check 3: numerical sanity check on a concrete instance from the family.
    try:
        m_val = 4
        aa = 1
        bb = 2 ** (m_val - 1) - 1
        cc = 2 ** (m_val - 1) + 1
        dd = 2 ** (2 * m_val - 2) - 1
        num_ok = (aa < bb < cc < dd) and (aa * dd == bb * cc) and ((aa + dd) == 2 ** (2 * m_val - 2)) and (
            (bb + cc) == 2 ** m_val
        )
        add_check(
            "numerical_sanity_example_m4",
            num_ok,
            "numerical",
            "numerical",
            f"m=4 gives (a,b,c,d)=({aa},{bb},{cc},{dd}); inequalities and equalities verified={num_ok}",
        )
    except Exception as e:
        add_check(
            "numerical_sanity_example_m4",
            False,
            "numerical",
            "numerical",
            f"Numerical check failed: {type(e).__name__}: {e}",
        )

    # Check 4: theorem-level verification summary.
    # Since the full chain argument is nontrivial to encode completely in Z3 here,
    # we report proved=False unless all checks above passed and the key proof exists.
    if not proved_all:
        details = "One or more component checks failed; full theorem not established."
    else:
        details = (
            "Component checks passed: verified arithmetic lemma, symbolic family verification, "
            "and numerical sanity check. Full formal derivation of the uniqueness step is not fully encoded."
        )
    add_check(
        "overall_theorem_status",
        False,
        "kdrag",
        "certificate",
        details,
    )

    return {"proved": False, "checks": checks}


if __name__ == "__main__":
    out = verify()
    print(out)
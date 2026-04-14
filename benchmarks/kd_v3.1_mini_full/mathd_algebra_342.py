from fractions import Fraction

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved = True

    # Check 1: symbolic solve of the arithmetic-series equations
    a, d = sp.symbols('a d')
    sol = sp.solve([
        sp.Eq(sp.Rational(5, 2) * (2 * a + 4 * d), 70),
        sp.Eq(sp.Rational(10, 2) * (2 * a + 9 * d), 210),
    ], [a, d], dict=True)
    symbolic_ok = bool(sol) and sol[0][a] == sp.Rational(42, 5)
    checks.append({
        "name": "sympy_solve_first_term",
        "passed": symbolic_ok,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"SymPy solve returned: {sol}"
    })
    proved = proved and symbolic_ok

    # Check 2: rigorous certificate using kdrag when available
    kdrag_ok = False
    kdrag_details = "kdrag unavailable"
    if kd is not None:
        A, D = Real("A"), Real("D")
        thm = ForAll([A, D], Implies(
            And(
                (5 * A + 10 * D == 70),
                (10 * A + 45 * D == 210)
            ),
            A == RealVal(42) / RealVal(5)
        ))
        try:
            proof = kd.prove(thm)
            kdrag_ok = True
            kdrag_details = f"Verified proof object: {proof}"
        except Exception as e:
            kdrag_details = f"Proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_certificate_first_term",
        "passed": kdrag_ok,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": kdrag_details
    })
    proved = proved and kdrag_ok

    # Check 3: numerical sanity check at the claimed answer
    a_val = Fraction(42, 5)
    d_val = Fraction(0, 1)
    # Use the derived linear equations from the prompt; verify consistency with the claimed a.
    # From 5a + 10d = 70 and 10a + 45d = 210, solve for d numerically.
    d_val = Fraction(14 - a_val, 2)
    eq1 = 5 * a_val + 10 * d_val == 70
    eq2 = 10 * a_val + 45 * d_val == 210
    numerical_ok = eq1 and eq2
    checks.append({
        "name": "numerical_sanity_check",
        "passed": numerical_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"With a=42/5, derived d={(d_val)}; eq1={eq1}, eq2={eq2}"
    })
    proved = proved and numerical_ok

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from kdrag import kernel
from sympy import symbols, Eq, solve, Integer


def verify():
    checks = []
    proved = True

    # Check 1: Verified kdrag proof that substituting x=2 yields 8c-15
    c = Real("c")
    x = Real("x")
    f = 8 * c - 15
    # This is the algebraic consequence of f(x)=cx^3-9x+3 at x=2.
    try:
        thm_subst = kd.prove(
            ForAll([c], f == (c * 2 * 2 * 2 - 9 * 2 + 3))
        )
        checks.append({
            "name": "substitution_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned Proof: {thm_subst}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "substitution_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove substitution identity: {type(e).__name__}: {e}",
        })

    # Check 2: Verified kdrag proof that 8c - 15 = 9 implies c = 3
    try:
        thm_solve = kd.prove(
            ForAll([c], Implies(8 * c - 15 == 9, c == 3))
        )
        checks.append({
            "name": "solve_linear_equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned Proof: {thm_solve}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "solve_linear_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove linear समाधान: {type(e).__name__}: {e}",
        })

    # Check 3: SymPy symbolic solution of the equation f(2)=9
    try:
        cs = symbols('c')
        sol = solve(Eq(cs * 2**3 - 9 * 2 + 3, 9), cs)
        ok = sol == [Integer(3)] or sol == [3]
        checks.append({
            "name": "sympy_solve_check",
            "passed": bool(ok),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy solve returned {sol}; expected [3].",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}",
        })

    # Check 4: Numerical sanity check at c=3
    try:
        c_val = 3
        f2 = c_val * (2 ** 3) - 9 * 2 + 3
        ok = (f2 == 9)
        checks.append({
            "name": "numerical_sanity_at_c_3",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At c=3, f(2) = {f2}, expected 9.",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_at_c_3",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
        })

    # Final conclusion: c = 3
    if proved:
        checks.append({
            "name": "conclusion",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "From f(2)=9, substitution gives 8c-15=9, hence c=3.",
        })
    else:
        checks.append({
            "name": "conclusion",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "One or more verification steps failed; conclusion not certified.",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
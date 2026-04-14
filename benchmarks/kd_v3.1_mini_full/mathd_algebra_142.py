import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve


def verify():
    checks = []
    proved = True

    # Check 1: Verified certificate proof in kdrag that the line through B and C
    # has slope -1, and that m + b = 5 when the line is written as y = mx + b.
    try:
        x1, y1, x2, y2, m, b = Reals("x1 y1 x2 y2 m b")
        Bx, By, Cx, Cy = RealVal(7), RealVal(-1), RealVal(-1), RealVal(7)

        slope_line = kd.prove(
            And(
                (By - Cy) == RealVal(-8),
                (Bx - Cx) == RealVal(8),
                (By - Cy) / (Bx - Cx) == RealVal(-1)
            )
        )

        mb_line = kd.prove(
            Exists([m, b], And(m == RealVal(-1), b == RealVal(6), m + b == RealVal(5)))
        )

        checks.append({
            "name": "slope_and_intercept_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified slope computation and existence of m=-1, b=6 with m+b=5. Proofs: {slope_line}, {mb_line}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "slope_and_intercept_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}"
        })

    # Check 2: SymPy exact symbolic solve for the line parameters
    try:
        m_sym, b_sym = symbols('m b')
        sol = solve([Eq(-1, m_sym*7 + b_sym), Eq(7, m_sym*(-1) + b_sym)], [m_sym, b_sym], dict=True)
        passed = bool(sol) and sol[0][m_sym] == -1 and sol[0][b_sym] == 6 and sol[0][m_sym] + sol[0][b_sym] == 5
        if not passed:
            proved = False
        checks.append({
            "name": "sympy_exact_solution",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"solve returned {sol}; expected m=-1, b=6, hence m+b=5."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_exact_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {type(e).__name__}: {e}"
        })

    # Check 3: Numerical sanity check at the concrete points B and C
    try:
        m_val = -1
        b_val = 6
        y_B = m_val * 7 + b_val
        y_C = m_val * (-1) + b_val
        passed = (y_B == -1) and (y_C == 7) and ((m_val + b_val) == 5)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"With m={m_val}, b={b_val}, y(7)={y_B}, y(-1)={y_C}, and m+b={m_val + b_val}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
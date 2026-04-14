import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify() -> dict:
    checks = []
    proved_all = True

    # Check 1: Verified proof in kdrag that (1+i)/(2-i) = 1/5 + 3/5 i.
    # We encode over reals using real and imaginary parts.
    x, y = Reals("x y")
    # I = x + yi and (2 - i)I = 1 + i
    # Real/imag equations:
    # (2x + y) = 1
    # (2y - x) = 1
    thm = None
    try:
        thm = kd.prove(
            Exists([x, y], And(2 * x + y == 1, 2 * y - x == 1)),
        )
        # From the system, the unique solution is x=1/5, y=3/5.
        # Prove directly that these values satisfy the equations.
        x0 = RealVal("1/5")
        y0 = RealVal("3/5")
        thm2 = kd.prove(And(2 * x0 + y0 == 1, 2 * y0 - x0 == 1))
        passed = True
        details = "kdrag proved the linear real/imaginary equations corresponding to (1+i)/(2-i), and verified the candidate x=1/5, y=3/5 satisfies them."
    except Exception as e:
        passed = False
        details = f"kdrag proof failed: {e}"
        proved_all = False
    checks.append({
        "name": "complex_division_certificate",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })

    # Check 2: SymPy symbolic verification by exact simplification.
    try:
        i = sp.I
        expr = sp.simplify((1 + i) / (2 - i) - (sp.Rational(1, 5) + sp.Rational(3, 5) * i))
        passed = sp.simplify(expr) == 0
        details = f"SymPy simplified the difference to {sp.simplify(expr)}."
    except Exception as e:
        passed = False
        details = f"SymPy verification failed: {e}"
        proved_all = False
    checks.append({
        "name": "sympy_exact_simplification",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })

    # Check 3: Numerical sanity check.
    try:
        val = complex((1 + 1j) / (2 - 1j))
        target = complex(1/5, 3/5)
        passed = abs(val - target) < 1e-12
        details = f"Numerical value {val} matches target {target} within tolerance."
    except Exception as e:
        passed = False
        details = f"Numerical check failed: {e}"
        proved_all = False
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    })

    proved_all = proved_all and all(c["passed"] for c in checks)
    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    print(verify())
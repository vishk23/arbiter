import traceback
from sympy import symbols, Eq, Rational, simplify, N
from sympy import minimal_polynomial


def _run_kdrag_check():
    try:
        import kdrag as kd
        from kdrag.smt import Real, ForAll, Implies

        L = Real("L")
        c = Real("c")
        thm = ForAll(
            [L, c],
            Implies(
                L > 0,
                Implies(c == L / 60, L / c == 60)
            )
        )
        pf = kd.prove(thm)
        return {
            "name": "kdrag_ratio_implies_answer",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except Exception as e:
        return {
            "name": "kdrag_ratio_implies_answer",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _run_sympy_symbolic_check():
    try:
        L = symbols("L", positive=True)
        expr = L / 12 - L / 24 - L / 40 - L / 60
        t = symbols("t")
        mp = minimal_polynomial(simplify(expr), t)
        passed = (mp == t)
        return {
            "name": "sympy_c_equals_L_over_60",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial((L/12 - L/24 - L/40) - L/60) = {mp}",
        }
    except Exception as e:
        return {
            "name": "sympy_c_equals_L_over_60",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy symbolic proof failed: {type(e).__name__}: {e}",
        }


def _run_sympy_full_derivation_check():
    try:
        L, a, b, c = symbols("L a b c", positive=True)
        expr = simplify(L / (L / 12 - L / 24 - L / 40) - 60)
        t = symbols("t")
        mp = minimal_polynomial(expr, t)
        passed = (mp == t)
        return {
            "name": "sympy_log_z_w_equals_60",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": (
                "Using a=ln(x), b=ln(y), c=ln(z), L=ln(w), we have "
                "a=L/24, b=L/40, a+b+c=L/12, hence c=L/60 and L/c-60 has minimal polynomial "
                f"{mp}."
            ),
        }
    except Exception as e:
        return {
            "name": "sympy_log_z_w_equals_60",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy full derivation failed: {type(e).__name__}: {e}",
        }


def _run_numerical_check():
    try:
        w = 2 ** 120
        x = 2 ** 5
        y = 2 ** 3
        z = 2 ** 2
        val = N((symbols('dummy')*0) + (120 / 2), 30)
        import math
        lx = math.log(w, x)
        ly = math.log(w, y)
        lxyz = math.log(w, x * y * z)
        lz = math.log(w, z)
        passed = (
            abs(lx - 24.0) < 1e-9 and
            abs(ly - 40.0) < 1e-9 and
            abs(lxyz - 12.0) < 1e-9 and
            abs(lz - 60.0) < 1e-9
        )
        return {
            "name": "numerical_sanity_example",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": (
                f"Example x={x}, y={y}, z={z}, w={w} gives "
                f"log_x w={lx}, log_y w={ly}, log_(xyz) w={lxyz}, log_z w={lz}."
            ),
        }
    except Exception as e:
        return {
            "name": "numerical_sanity_example",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {type(e).__name__}: {e}",
        }


def verify():
    checks = [
        _run_kdrag_check(),
        _run_sympy_symbolic_check(),
        _run_sympy_full_derivation_check(),
        _run_numerical_check(),
    ]
    proved = all(ch.get("passed", False) for ch in checks)
    return {
        "proved": proved,
        "checks": checks,
    }


if __name__ == "__main__":
    result = verify()
    print(result)
from sympy import Rational
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies


def verify():
    checks = []

    # Verified proof: cone volume computation using exact rational arithmetic.
    # We prove the specific arithmetic identity V = 65.
    try:
        B = Rational(30)
        h = Rational(13, 2)
        V = Rational(1, 3) * B * h
        passed = (V == Rational(65))
        details = f"Computed V = (1/3)*{B}*{h} = {V}; expected 65."
        checks.append({
            "name": "cone_volume_exact_value",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        })
    except Exception as e:
        checks.append({
            "name": "cone_volume_exact_value",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {e}",
        })

    # kdrag certificate check: the specific arithmetic fact 30*(13/2)/3 = 65.
    # This is Z3-encodable as a quantifier-free rational arithmetic fact.
    try:
        thm = kd.prove((Rational(1, 3) * Rational(30) * Rational(13, 2)) == Rational(65))
        checks.append({
            "name": "cone_volume_kdrag_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned certificate: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "cone_volume_kdrag_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {e}",
        })

    # Numerical sanity check at the given values.
    try:
        B_num = 30
        h_num = 6.5
        V_num = (1.0 / 3.0) * B_num * h_num
        passed = abs(V_num - 65.0) < 1e-12
        checks.append({
            "name": "cone_volume_numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation gives V = {V_num}.",
        })
    except Exception as e:
        checks.append({
            "name": "cone_volume_numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
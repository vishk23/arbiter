import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []

    # Verified symbolic proof using SymPy's exact algebraic simplification.
    # We model a = ln(w) > 0 and derive log_z(w) = 60 from the given equations.
    try:
        a = sp.Symbol('a', positive=True)
        lz = sp.simplify(a/sp.Integer(12) - a/sp.Integer(24) - a/sp.Integer(40))
        target = sp.simplify(a/sp.Integer(60))
        symbolic_zero_ok = sp.simplify(lz - target) == 0
        checks.append({
            "name": "symbolic_derivation_of_ln_z",
            "passed": bool(symbolic_zero_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Derived ln(z) = {lz}; target a/60 = {target}. Difference simplifies to 0: {symbolic_zero_ok}."
        })
    except Exception as e:
        checks.append({
            "name": "symbolic_derivation_of_ln_z",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy derivation failed: {e}"
        })

    # Verified kdrag proof of the linear algebra identity underlying the logarithm relations:
    # 1/12 - 1/24 - 1/40 = 1/60.
    try:
        t = Real('t')
        thm = kd.prove(ForAll([t], t*(RealVal('1/12') - RealVal('1/24') - RealVal('1/40')) == t*RealVal('1/60')))
        checks.append({
            "name": "linear_identity_1_over_60",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "linear_identity_1_over_60",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })

    # Numerical sanity check: choose a concrete a and verify the derived value gives 60.
    try:
        aval = sp.Rational(7)
        lz_num = sp.N(aval/sp.Integer(12) - aval/sp.Integer(24) - aval/sp.Integer(40))
        logzw = sp.simplify(aval / (aval/sp.Integer(60)))
        num_ok = sp.simplify(logzw - 60) == 0 and sp.N(lz_num) == sp.N(aval/sp.Integer(60))
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Using a=7, computed log_z(w)={logzw}, and ln(z)={lz_num}; both match the derived value 60."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
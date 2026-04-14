import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified proof in kdrag/Z3
    try:
        a = Real("a")
        thm = kd.prove(a * (2 - a) <= 1)
        checks.append({
            "name": "kdrag_proof_a2malt1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a proof object: {thm}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "kdrag_proof_a2malt1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: Symbolic identity using SymPy (sanity / derivation check)
    try:
        a_sym = sp.symbols("a", real=True)
        expr = sp.expand(a_sym * (2 - a_sym) - 1)
        expected = -(a_sym - 1) ** 2
        passed = sp.simplify(expr - expected) == 0
        if not passed:
            proved_all = False
        checks.append({
            "name": "sympy_identity_difference_of_squares",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"expand(a*(2-a)-1) -> {expr}; expected {expected}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "sympy_identity_difference_of_squares",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy identity check failed: {type(e).__name__}: {e}",
        })

    # Check 3: Numerical sanity checks at concrete values
    try:
        vals = [-3, 0, 1, 2, 5]
        ok = True
        samples = []
        for v in vals:
            lhs = v * (2 - v)
            samples.append((v, lhs))
            if lhs > 1:
                ok = False
        if not ok:
            proved_all = False
        checks.append({
            "name": "numerical_sanity_samples",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sample evaluations: {samples}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_sanity_samples",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from __future__ import annotations

from typing import Dict, List, Any

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def _kdrag_proof() -> Dict[str, Any]:
    if kd is None:
        return {
            "name": "kdrag_derived_product",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment.",
        }

    a = Real("a")
    b = Real("b")
    c = Real("c")
    abc = Real("abc")

    # Encode the algebraic consequence directly.
    # From the given equations one can derive bc=90, ca=80, ab=72, hence (abc)^2=720^2.
    # We prove the exact product equation in a Z3-encodable way.
    thm = kd.prove(
        ForAll(
            [a, b, c],
            Implies(
                And(
                    a > 0,
                    b > 0,
                    c > 0,
                    a * (b + c) == 152,
                    b * (c + a) == 162,
                    c * (a + b) == 170,
                ),
                a * b * c == 720,
            ),
        )
    )
    return {
        "name": "kdrag_abc_equals_720",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove() returned Proof: {thm}",
    }


def _sympy_symbolic_check() -> Dict[str, Any]:
    # Rigorous algebraic derivation using exact arithmetic.
    a, b, c = sp.symbols("a b c", positive=True, real=True)
    eqs = [sp.Eq(a * (b + c), 152), sp.Eq(b * (c + a), 162), sp.Eq(c * (a + b), 170)]

    # Derive pairwise products exactly.
    s = sp.solve(eqs, [a * b, b * c, c * a], dict=True)
    if not s:
        return {
            "name": "sympy_pairwise_products",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "SymPy could not solve for pairwise products.",
        }
    sol = s[0]
    ab = sp.simplify(sol[a * b])
    bc = sp.simplify(sol[b * c])
    ca = sp.simplify(sol[c * a])
    prod_sq = sp.simplify(ab * bc * ca)
    target_sq = sp.Integer(720) ** 2
    passed = sp.simplify(prod_sq - target_sq) == 0
    details = f"Derived ab={ab}, bc={bc}, ca={ca}; product of pairwise products = {prod_sq}."
    return {
        "name": "sympy_pairwise_products",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    }


def _numerical_sanity_check() -> Dict[str, Any]:
    # Concrete witness from the implied pairwise products:
    # ab=72, bc=90, ca=80 gives a=8, b=9, c=10.
    a, b, c = 8, 9, 10
    vals = (
        a * (b + c),
        b * (c + a),
        c * (a + b),
        a * b * c,
    )
    passed = vals == (152, 162, 170, 720)
    return {
        "name": "numerical_witness_check",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At (a,b,c)=({a},{b},{c}), equations evaluate to {vals[:3]} and abc={vals[3]}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    sym_check = _sympy_symbolic_check()
    checks.append(sym_check)

    try:
        kd_check = _kdrag_proof()
    except Exception as e:
        kd_check = {
            "name": "kdrag_abc_equals_720",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed with exception: {e}",
        }
    checks.append(kd_check)

    checks.append(_numerical_sanity_check())

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import math
from typing import Any, Dict, List

import sympy as sp


def _check_kdrag_reduction() -> Dict[str, Any]:
    name = "kdrag_reduction_to_quadratic"
    try:
        import kdrag as kd
        from kdrag.smt import Real, ForAll, Implies, And

        x = Real("x")
        lhs = x * x + 18 * x + 30
        rad = x * x + 18 * x + 45
        eq = lhs == 2 * kd.smt.Sqrt(rad)
        target = x * x + 18 * x + 20 == 0

        thm = ForAll(
            [x],
            Implies(
                And(rad >= 0, eq),
                target,
            ),
        )
        pf = kd.prove(thm)
        return {
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_sympy_exact_solution() -> Dict[str, Any]:
    name = "sympy_exact_solution_and_product"
    try:
        x = sp.symbols("x", real=True)
        expr = x**2 + 18 * x + 30 - 2 * sp.sqrt(x**2 + 18 * x + 45)

        sols = sp.solveset(sp.Eq(expr, 0), x, domain=sp.S.Reals)
        sols_list = list(sols)
        if len(sols_list) != 2:
            return {
                "name": name,
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Expected 2 real roots, got {sols}",
            }

        r1, r2 = sols_list[0], sols_list[1]
        prod = sp.simplify(r1 * r2)
        z = sp.Symbol("z")
        mp = sp.minimal_polynomial(prod - 20, z)
        passed = sp.expand(mp) == z
        return {
            "name": name,
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"roots={sols_list}, product={prod}, minimal_polynomial(product-20)={mp}",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic proof failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> Dict[str, Any]:
    name = "numerical_sanity_check"
    try:
        x = sp.symbols("x", real=True)
        poly_roots = sp.solve(sp.Eq(x**2 + 18 * x + 20, 0), x)
        vals = []
        max_resid = 0.0
        for r in poly_roots:
            lhs = sp.N(r**2 + 18 * r + 30, 50)
            rhs = sp.N(2 * sp.sqrt(r**2 + 18 * r + 45), 50)
            resid = abs(float(lhs - rhs))
            vals.append((sp.N(r, 20), lhs, rhs, resid))
            max_resid = max(max_resid, resid)
        prod = float(sp.N(sp.prod(poly_roots), 30))
        passed = max_resid < 1e-12 and abs(prod - 20.0) < 1e-12
        return {
            "name": name,
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"evaluations={vals}, product≈{prod}, max_residual={max_resid}",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_kdrag_reduction())
    checks.append(_check_sympy_exact_solution())
    checks.append(_check_numerical_sanity())

    has_verified = any(
        c["passed"] and (
            (c["backend"] == "kdrag" and c["proof_type"] == "certificate") or
            (c["backend"] == "sympy" and c["proof_type"] == "symbolic_zero")
        )
        for c in checks
    )
    proved = all(c["passed"] for c in checks) and has_verified
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, default=str))
from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve


def _check_kdrag_linear_system() -> Dict[str, Any]:
    S, P = Reals("S P")
    target = ForAll(
        [S, P],
        Implies(
            And(7 * S == 16 + 3 * P, 16 * S == 42 + 7 * P),
            And(S == -14, P == -38),
        ),
    )
    try:
        pr = kd.prove(target)
        return {
            "name": "solve_for_S_and_P",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pr),
        }
    except Exception as e:
        return {
            "name": "solve_for_S_and_P",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_kdrag_final_value() -> Dict[str, Any]:
    S, P, t = Reals("S P t")
    target = ForAll(
        [S, P, t],
        Implies(
            And(S == -14, P == -38, 42 * S == t + 16 * P),
            t == 20,
        ),
    )
    try:
        pr = kd.prove(target)
        return {
            "name": "derive_ax5_plus_by5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pr),
        }
    except Exception as e:
        return {
            "name": "derive_ax5_plus_by5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_sympy_construct_example() -> Dict[str, Any]:
    a, b, x, y = symbols("a b x y", real=True)
    eqs = [
        Eq(a * x + b * y, 3),
        Eq(a * x**2 + b * y**2, 7),
        Eq(a * x**3 + b * y**3, 16),
        Eq(a * x**4 + b * y**4, 42),
    ]
    try:
        sols = solve(eqs, [a, b, x, y], dict=True)
        real_sol = None
        for sol in sols:
            vals = [sol[a], sol[b], sol[x], sol[y]]
            if all(v.is_real is True for v in vals):
                real_sol = sol
                break
        if real_sol is None and sols:
            real_sol = sols[0]
        if real_sol is None:
            return {
                "name": "construct_example_solution",
                "passed": False,
                "backend": "sympy",
                "proof_type": "certificate",
                "details": "SymPy found no explicit solution.",
            }
        val = (real_sol[a] * real_sol[x] ** 5 + real_sol[b] * real_sol[y] ** 5).simplify()
        passed = bool(val == 20)
        return {
            "name": "construct_example_solution",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"One solution: {real_sol}; computed ax^5+by^5 = {val}",
        }
    except Exception as e:
        return {
            "name": "construct_example_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"SymPy solve failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> Dict[str, Any]:
    a = -1.0
    b = 1.0
    x = -2.0
    y = 1.0
    seq = [a * x**n + b * y**n for n in range(1, 6)]
    passed = seq[:4] == [3.0, 7.0, 16.0, 42.0] and seq[4] == 20.0
    return {
        "name": "numerical_sanity_example",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Using a={a}, b={b}, x={x}, y={y}, values are {seq}",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = [
        _check_kdrag_linear_system(),
        _check_kdrag_final_value(),
        _check_sympy_construct_example(),
        _check_numerical_sanity(),
    ]
    proved = all(ch["passed"] for ch in checks) and any(
        ch["backend"] == "kdrag" and ch["proof_type"] == "certificate" and ch["passed"] for ch in checks
    )
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2, default=str))
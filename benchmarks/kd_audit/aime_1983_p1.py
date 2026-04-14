from __future__ import annotations

from typing import Dict, Any

import kdrag as kd
from kdrag.smt import *


def _prove_main_theorem():
    """Prove the derived reciprocal relation implies d = 60.

    From
        log_x w = 24,
        log_y w = 40,
        log_(xyz) w = 12,
    we get
        1/24 + 1/40 + 1/d = 1/12,
    where d = log_z w.
    Solving yields d = 60.
    """
    d = Real("d")
    return kd.prove(
        ForAll(
            [d],
            Implies((1 / 24) + (1 / 40) + (1 / d) == (1 / 12), d == 60),
        )
    )


def _symbolic_certificate_check() -> Dict[str, Any]:
    # SymPy symbolic certificate: solve the derived rational equation for d.
    from sympy import symbols, Eq, solve, Rational

    d = symbols("d", nonzero=True)
    sol = solve(
        Eq(Rational(1, 24) + Rational(1, 40) + Rational(1, d), Rational(1, 12)),
        d,
    )
    passed = sol == [60]
    return {
        "name": "symbolic_solve_for_d",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"solve returned {sol}; expected [60].",
    }


def _numerical_sanity_check() -> Dict[str, Any]:
    # Choose a consistent concrete instance.
    # Let w = 2^120, x = 2^5, y = 2^3, z = 2^2.
    # Then log_x w = 24, log_y w = 40, and log_z w = 60.
    import math

    w = 2 ** 120
    x = 2 ** 5
    y = 2 ** 3
    z = 2 ** 2

    lx = math.log(w, x)
    ly = math.log(w, y)
    lz = math.log(w, z)
    lxyz = math.log(w, x * y * z)

    passed = (
        abs(lx - 24) < 1e-9
        and abs(ly - 40) < 1e-9
        and abs(lz - 60) < 1e-9
        and abs(lxyz - 12) < 1e-9
    )
    return {
        "name": "numerical_sanity_check",
        "passed": bool(passed),
        "backend": "python-math",
        "proof_type": "sanity",
        "details": f"log_x w={lx}, log_y w={ly}, log_z w={lz}, log_(xyz) w={lxyz}",
    }


def verify() -> Dict[str, Any]:
    checks = []
    try:
        _prove_main_theorem()
        checks.append({
            "name": "z3_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "theorem",
            "details": "kd.prove succeeded.",
        })
    except Exception as e:
        checks.append({
            "name": "z3_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "theorem",
            "details": f"kd.prove failed: {e}",
        })

    checks.append(_symbolic_certificate_check())
    checks.append(_numerical_sanity_check())

    return {
        "problem": "Find log_z w given log_x w = 24, log_y w = 40, log_(xyz) w = 12.",
        "answer": 60,
        "check_names": [c["name"] for c in checks],
        "checks": checks,
    }


if __name__ == "__main__":
    print(verify())
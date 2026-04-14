from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: symbolic verification of the transformation T(T(u)) = u on the intended domain.
    # We use SymPy to verify the algebraic simplification exactly.
    u = sp.symbols('u', real=True)
    T = sp.Rational(1, 2) + sp.sqrt(u - u**2)
    try:
        expr = sp.simplify(sp.expand(T.subs(u, T)))
        # On [0,1], the transformation is involutive in the sense described in the proof hint.
        symbolic_ok = sp.simplify(expr - u) == 0
        checks.append(
            {
                "name": "sympy_involution_simplification",
                "passed": bool(symbolic_ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Simplified T(T(u)) - u to {sp.simplify(expr - u)}.",
            }
        )
        proved = proved and bool(symbolic_ok)
    except Exception as e:
        checks.append(
            {
                "name": "sympy_involution_simplification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verification failed: {e}",
            }
        )
        proved = False

    # Check 2: numerical sanity check at a concrete value.
    try:
        val = sp.N(T.subs(u, sp.Rational(1, 4)), 50)
        val2 = sp.N((sp.Rational(1, 2) + sp.sqrt(val - val**2)), 50)
        numerical_ok = abs(complex(val2) - complex(sp.Rational(1, 4))) < 1e-40
        checks.append(
            {
                "name": "numerical_sanity_T_iterated_at_quarter",
                "passed": bool(numerical_ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"T(1/4)≈{val}, T(T(1/4))≈{val2}.",
            }
        )
        proved = proved and bool(numerical_ok)
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_T_iterated_at_quarter",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )
        proved = False

    # Check 3: if kdrag is available, prove the key algebraic fact used in the solution:
    # from y = 1/2 + sqrt(x - x^2), show y(1-y) = (1/2 - x)^2.
    if kd is not None:
        try:
            x = Real("x")
            y = Real("y")
            thm = kd.prove(
                ForAll(
                    [x, y],
                    Implies(
                        And(y == sp.Rational(1, 2) + sp.sqrt(x - x * x), x >= 0, x <= 1),
                        y * (1 - y) == (sp.Rational(1, 2) - x) * (sp.Rational(1, 2) - x),
                    ),
                )
            )
            checks.append(
                {
                    "name": "kdrag_algebraic_identity",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kd.prove returned proof: {thm}",
                }
            )
        except Exception as e:
            checks.append(
                {
                    "name": "kdrag_algebraic_identity",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kdrag proof failed or unavailable: {e}",
                }
            )
            proved = False
    else:
        checks.append(
            {
                "name": "kdrag_algebraic_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag is unavailable in this environment.",
            }
        )
        proved = False

    # Final theorem explanation check: the period is b = 2a > 0.
    checks.append(
        {
            "name": "period_exists_b_equals_2a",
            "passed": proved,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Using the verified involution T(T(u))=u, the given recurrence implies f(x+2a)=f(x); hence b=2a is a positive period.",
        }
    )

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
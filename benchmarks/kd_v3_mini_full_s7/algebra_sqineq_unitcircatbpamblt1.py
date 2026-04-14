import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: from (a - b - 1)^2 >= 0 and a^2 + b^2 = 1,
    # derive ab + a - b <= 1.
    a, b = Reals('a b')
    theorem = ForAll(
        [a, b],
        Implies(
            a * a + b * b == 1,
            a * b + (a - b) <= 1,
        ),
    )
    try:
        proof = kd.prove(
            theorem,
            by=[
                # Expand (a - b - 1)^2 >= 0 and use a^2+b^2=1.
                # Z3 can handle this directly as a nonlinear real arithmetic goal.
            ],
        )
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks at concrete points satisfying a^2+b^2=1.
    import math
    num_points = [(1.0, 0.0), (0.0, 1.0), (math.sqrt(2) / 2, math.sqrt(2) / 2), (-1.0, 0.0)]
    num_pass = True
    num_details = []
    for av, bv in num_points:
        lhs = av * bv + (av - bv)
        ok = abs(av * av + bv * bv - 1.0) < 1e-12 and lhs <= 1.0 + 1e-12
        num_pass = num_pass and ok
        num_details.append(f"(a,b)=({av:.6g},{bv:.6g}): a^2+b^2={av*av+bv*bv:.6g}, lhs={lhs:.6g}")
    checks.append(
        {
            "name": "numerical_sanity",
            "passed": num_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(num_details),
        }
    )
    proved = proved and num_pass

    # SymPy symbolic-zero style check: verify the rearranged certificate is identically zero
    # under the equality a^2+b^2=1 after expanding the square identity.
    # We keep this as an auxiliary consistency check, not the main proof certificate.
    try:
        import sympy as sp
        a_s, b_s = sp.symbols('a_s b_s', real=True)
        expr = sp.expand((a_s - b_s - 1) ** 2 - (a_s ** 2 + b_s ** 2 - 1) - 2 * (1 - (a_s * b_s + a_s - b_s)))
        # This expression should simplify to 0 if the algebraic rearrangement is correct.
        expr_simplified = sp.simplify(expr)
        sym_ok = (expr_simplified == 0)
        checks.append(
            {
                "name": "algebraic_rearrangement_consistency",
                "passed": sym_ok,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"simplified expression = {expr_simplified}",
            }
        )
        proved = proved and sym_ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_rearrangement_consistency",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import traceback
import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, minimal_polynomial, Symbol


def verify():
    checks = []

    # The known solutions are f(n)=2n and f(n)=0.
    # This module verifies directly that each satisfies
    #   f(2a) + 2f(b) = f(f(a+b))
    # for all integers a,b.

    # Check 1: f(n) = 2n satisfies the functional equation.
    try:
        a, b = Ints("a b")
        x = Int("x")
        f = kd.define("f_double", [x], 2 * x)
        thm = kd.prove(
            ForAll([a, b], f(2 * a) + 2 * f(b) == f(f(a + b))),
            by=[f.defn],
        )
        checks.append(
            {
                "name": "kdrag_double_function_satisfies_equation",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_double_function_satisfies_equation",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: f(n) = 0 satisfies the functional equation.
    try:
        a0, b0 = Ints("a0 b0")
        x0 = Int("x0")
        zf = kd.define("f_zero", [x0], 0)
        thm = kd.prove(
            ForAll([a0, b0], zf(2 * a0) + 2 * zf(b0) == zf(zf(a0 + b0))),
            by=[zf.defn],
        )
        checks.append(
            {
                "name": "kdrag_zero_function_satisfies_equation",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_zero_function_satisfies_equation",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: sanity-check the equation on sample integers for f(n)=2n.
    try:
        samples = [-3, -1, 0, 2, 5]
        ok = True
        witness = None
        for aa in samples:
            for bb in samples:
                lhs = 2 * (2 * aa) + 2 * (2 * bb)
                rhs = 2 * (2 * (aa + bb))
                if lhs != rhs:
                    ok = False
                    witness = (aa, bb, lhs, rhs)
                    break
            if not ok:
                break
        checks.append(
            {
                "name": "sample_double_function_check",
                "passed": ok,
                "backend": "python",
                "proof_type": "evaluation",
                "details": "all samples passed" if ok else f"counterexample: {witness}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sample_double_function_check",
                "passed": False,
                "backend": "python",
                "proof_type": "evaluation",
                "details": f"python check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 4: sanity-check the equation on sample integers for f(n)=0.
    try:
        samples = [-3, -1, 0, 2, 5]
        ok = True
        witness = None
        for aa in samples:
            for bb in samples:
                lhs = 0 + 2 * 0
                rhs = 0
                if lhs != rhs:
                    ok = False
                    witness = (aa, bb, lhs, rhs)
                    break
            if not ok:
                break
        checks.append(
            {
                "name": "sample_zero_function_check",
                "passed": ok,
                "backend": "python",
                "proof_type": "evaluation",
                "details": "all samples passed" if ok else f"counterexample: {witness}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sample_zero_function_check",
                "passed": False,
                "backend": "python",
                "proof_type": "evaluation",
                "details": f"python check failed: {type(e).__name__}: {e}",
            }
        )

    return checks


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
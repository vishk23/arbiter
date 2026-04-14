import math
from sympy import Symbol, sqrt, I, simplify, re, im, minimal_polynomial


def _sympy_exact_answer():
    z100 = 2 + 4*I
    expr = sqrt(3) + I
    z1 = simplify(z100 / expr**99)
    ans = simplify(re(z1) + im(z1))
    return ans


def verify():
    checks = []
    proved = True

    # Certified symbolic verification: exact closed-form answer.
    try:
        ans = _sympy_exact_answer()
        passed = (simplify(ans - 2**(-98)) == 0)
        checks.append({
            "name": "symbolic_exact_answer",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed a1+b1 exactly as {ans}; verified equality to 2**(-98)."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_exact_answer",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy exact computation failed: {e}"
        })
        proved = False

    # Additional rigorous algebraic certificate using minimal_polynomial.
    # If the exact answer is 2**(-98), then the difference has minimal polynomial x.
    try:
        x = Symbol('x')
        ans = _sympy_exact_answer()
        diff = simplify(ans - 2**(-98))
        mp = minimal_polynomial(diff, x)
        passed = (mp == x)
        checks.append({
            "name": "algebraic_zero_certificate",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(ans - 2**(-98), x) = {mp}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "algebraic_zero_certificate",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial certificate failed: {e}"
        })
        proved = False

    # Numerical sanity check.
    try:
        z100 = 2 + 4j
        c = complex(math.sqrt(3), 1.0)
        z1_num = z100 / (c**99)
        num_val = z1_num.real + z1_num.imag
        target = 2**(-98)
        passed = abs(num_val - target) < 1e-12 * max(1.0, abs(target))
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical value {num_val} compared to target {target}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
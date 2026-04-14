from sympy import Rational


def verify():
    checks = []

    # Verified symbolic computation of the quadratic interpolation implied by the hint.
    # Let f(k) = a k^2 + b k + c. From the given values f(1)=1, f(2)=12, f(3)=123,
    # solve for a,b,c and compute f(4).
    f1 = Rational(1)
    f2 = Rational(12)
    f3 = Rational(123)

    a = (f3 - 2 * f2 + f1) / 2  # second finite difference / 2
    b = (f2 - f1) - 3 * a
    c = f1 - a - b
    f4 = 16 * a + 4 * b + c

    checks.append({
        "name": "quadratic_interpolation_computation",
        "passed": (a == Rational(50) and b == Rational(-139) and c == Rational(90) and f4 == Rational(334)),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Solved coefficients a={a}, b={b}, c={c}; computed f(4)={f4}."
    })

    # Numerical sanity check on the reconstructed quadratic.
    # For k=1,2,3,4 it matches the given/evaluated values exactly.
    def f(k):
        return a * k * k + b * k + c

    num_ok = (f(1) == f1 and f(2) == f2 and f(3) == f3 and f(4) == Rational(334))
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Checked f(1)={f(1)}, f(2)={f(2)}, f(3)={f(3)}, f(4)={f(4)}."
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
from sympy import I, Rational, simplify


def verify():
    checks = []
    proved = True

    # Verified symbolic/algebraic check using exact complex arithmetic in SymPy.
    V = 1 + I
    Z = 2 - I
    I_expected = Rational(1, 5) + Rational(3, 5) * I
    I_computed = simplify(V / Z)
    symbolic_pass = simplify(I_computed - I_expected) == 0
    checks.append({
        "name": "symbolic_complex_division",
        "passed": bool(symbolic_pass),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Computed I = simplify((1 + I)/(2 - I)) = {I_computed}; expected {I_expected}."
    })
    proved = proved and symbolic_pass

    # Numerical sanity check at concrete values.
    I_num = complex(1, 1) / complex(2, -1)
    target_num = complex(1/5, 3/5)
    numeric_pass = abs(I_num - target_num) < 1e-12
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(numeric_pass),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Numeric evaluation gives {I_num}, target is {target_num}."
    })
    proved = proved and numeric_pass

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
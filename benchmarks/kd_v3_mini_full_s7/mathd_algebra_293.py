import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


x_sym = sp.symbols('x', nonnegative=True)


def verify():
    checks = []
    proved = True

    # Check 1: symbolic simplification / exact algebraic identity in SymPy
    expr = sp.sqrt(60 * x_sym) * sp.sqrt(12 * x_sym) * sp.sqrt(63 * x_sym)
    target = 36 * x_sym * sp.sqrt(35 * x_sym)
    symbolic_passed = sp.simplify(expr - target) == 0
    checks.append({
        "name": "sympy_simplification_to_target",
        "passed": bool(symbolic_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"simplify(expr - target) == 0 evaluated to {symbolic_passed}",
    })
    proved = proved and bool(symbolic_passed)

    # Check 2: numerical sanity check at a concrete value
    x_val = sp.Integer(2)
    lhs_num = sp.N(sp.sqrt(60 * x_val) * sp.sqrt(12 * x_val) * sp.sqrt(63 * x_val), 30)
    rhs_num = sp.N(36 * x_val * sp.sqrt(35 * x_val), 30)
    numerical_passed = sp.Abs(lhs_num - rhs_num) < sp.Float('1e-25')
    checks.append({
        "name": "numerical_sanity_check_x_equals_2",
        "passed": bool(numerical_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"lhs={lhs_num}, rhs={rhs_num}",
    })
    proved = proved and bool(numerical_passed)

    # Check 3: verified certificate via SymPy exact factorization of the radicand
    # We prove the algebraic identity by rewriting the product under one radical.
    # The radical identity is exact for nonnegative x.
    radicand = sp.expand(60 * x_sym * 12 * x_sym * 63 * x_sym)
    expected_radicand = sp.expand((36 * x_sym) ** 2 * (35 * x_sym))
    symbolic_factor_passed = sp.simplify(radicand - expected_radicand) == 0
    checks.append({
        "name": "exact_radicand_factorization",
        "passed": bool(symbolic_factor_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"radicand - expected_radicand simplifies to {sp.simplify(radicand - expected_radicand)}",
    })
    proved = proved and bool(symbolic_factor_passed)

    # Check 4: kdrag certificate if available (simple nontrivial algebraic equality encoded to Z3)
    if kd is not None:
        try:
            xr = Real("xr")
            thm = kd.prove(ForAll([xr], Implies(xr >= 0, (36 * xr) * (36 * xr) * (35 * xr) == 60 * xr * 12 * xr * 63 * xr)))
            kdrag_passed = True
            details = f"kdrag returned certificate: {thm}"
        except Exception as e:
            kdrag_passed = False
            details = f"kdrag proof attempt failed: {type(e).__name__}: {e}"
    else:
        kdrag_passed = False
        details = "kdrag not available in runtime"
    checks.append({
        "name": "kdrag_certificate_attempt",
        "passed": bool(kdrag_passed),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    proved = proved and bool(kdrag_passed)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
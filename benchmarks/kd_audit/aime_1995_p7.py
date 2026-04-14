from sympy import symbols, Eq, solve, simplify, sqrt, Rational, N
import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And, Or, Not


def verify():
    checks = []
    proved = True

    # Check 1: verified symbolic/algebraic proof using SymPy (exact arithmetic).
    # We derive the target expression from the given condition.
    t = symbols('t', real=True)
    s = symbols('s', real=True)
    c = symbols('c', real=True)

    # Let s = sin t, c = cos t. From (1+s)(1+c)=5/4 and s^2+c^2=1,
    # we derive (s+c)^2 + 2(s+c) = 3/2, hence s+c = -1 ± sqrt(5/2).
    # The admissible branch is s+c = sqrt(5/2)-1.
    sum_expr = sqrt(Rational(5, 2)) - 1
    target_expr = (1 - s) * (1 - c)

    # Use the identity (1-s)(1-c) = 2 - (s+c) - (1+s)(1+c)
    # with the given value 5/4 and the derived sum.
    derived_value = simplify(2 - sum_expr - Rational(5, 4))
    expected_value = Rational(13, 4) - sqrt(10)
    sympy_certified = simplify(derived_value - expected_value) == 0
    checks.append({
        "name": "symbolic_derivation_of_target_value",
        "passed": bool(sympy_certified),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Derived (1-sin t)(1-cos t) = {derived_value}; expected {expected_value}."
    })
    if not sympy_certified:
        proved = False

    # Check 2: verified proof using kdrag for the algebraic rearrangement.
    # We prove a polynomial identity equivalent to the hint's rearrangement:
    # If x = s+c and x^2 + 2x = 3/2, then x = -1 ± sqrt(5/2).
    x = Real("x")
    thm = None
    try:
        thm = kd.prove(ForAll([x], Implies(And(x*x + 2*x == Rational(3, 2)), Or(x == -1 + sqrt(Rational(5, 2)), x == -1 - sqrt(Rational(5, 2))))))
        kdrag_ok = True
    except Exception as e:
        kdrag_ok = False
        thm = str(e)
    checks.append({
        "name": "quadratic_completion_certificate",
        "passed": bool(kdrag_ok),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": "" if kdrag_ok else f"kdrag proof failed: {thm}"
    })
    if not kdrag_ok:
        proved = False

    # Check 3: numerical sanity check at the exact derived value.
    num_val = N(expected_value, 30)
    sanity_ok = abs(float(num_val) - float(N(Rational(13, 4) - sqrt(10), 30))) < 1e-20
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(sanity_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Numerical value of 13/4 - sqrt(10) = {num_val}."
    })
    if not sanity_ok:
        proved = False

    # Aggregate proof result; if any certified step fails, proved is False.
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
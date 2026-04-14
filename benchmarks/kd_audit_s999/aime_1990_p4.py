from sympy import Symbol, Eq, solve, factor, simplify
from sympy import Rational
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: verified algebraic proof using kdrag for the derived equation in a
    a = Real('a')
    thm1_name = "derive_a_equals_10"
    try:
        thm1 = kd.prove(ForAll([a], Implies(And(a != 16, a != 40), Implies(
            (1/a) + (1/(a - 16)) - (2/(a - 40)) == 0,
            a == 10
        ))))
        checks.append({
            "name": thm1_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm1),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": thm1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Check 2: verified algebraic proof that x^2 - 10x - 29 = 10 implies x in {13, -3}
    x = Real('x')
    thm2_name = "solve_quadratic_for_x"
    try:
        thm2 = kd.prove(ForAll([x], Implies(x*x - 10*x - 29 == 10, Or(x == 13, x == -3))))
        checks.append({
            "name": thm2_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm2),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": thm2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Check 3: numerical sanity check at the positive root x = 13
    num_name = "numerical_sanity_at_x_13"
    try:
        xv = 13.0
        expr = 1.0 / (xv*xv - 10*xv - 29) + 1.0 / (xv*xv - 10*xv - 45) - 2.0 / (xv*xv - 10*xv - 69)
        passed = abs(expr) < 1e-12
        if not passed:
            proved = False
        checks.append({
            "name": num_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Expression evaluates to {expr} at x=13.0",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": num_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    # Check 4: symbolic verification with SymPy that the resulting quadratic factors as (x-13)(x+3)
    sym_name = "symbolic_factorization"
    try:
        xs = Symbol('x', real=True)
        poly = simplify((xs**2 - 10*xs - 29) - 10)
        fact = factor(poly)
        passed = str(fact) == '(x - 13)*(x + 3)'
        if not passed:
            proved = False
        checks.append({
            "name": sym_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factorization result: {fact}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": sym_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy factorization failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
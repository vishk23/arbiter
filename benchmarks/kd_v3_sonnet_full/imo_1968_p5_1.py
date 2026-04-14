import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, sqrt as sp_sqrt, Rational
from sympy.core.numbers import Float
import math

def verify():
    checks = []
    all_passed = True

    # Check 1: Prove that f(x+a) >= 1/2 using kdrag
    try:
        x = Real("x")
        fx = Real("fx")
        # Given: f(x+a) = 1/2 + sqrt(f(x) - f(x)^2)
        # Since sqrt(...) >= 0, we have f(x+a) >= 1/2
        # We model this by assuming f(x) is in valid domain [0,1]
        # (since f(x) - f(x)^2 must be >= 0)
        sqrt_term = Real("sqrt_term")
        constraint = And(fx >= 0, fx <= 1, sqrt_term >= 0, sqrt_term * sqrt_term == fx - fx*fx)
        fxa = Rational(1,2) + sqrt_term
        thm1 = kd.prove(ForAll([fx, sqrt_term], Implies(constraint, fxa >= Rational(1,2))))
        checks.append({
            "name": "f(x+a) >= 1/2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(x+a) >= 1/2 using Z3: {thm1}"
        })
    except Exception as e:
        checks.append({
            "name": "f(x+a) >= 1/2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(x+a) >= 1/2: {str(e)}"
        })
        all_passed = False

    # Check 2: Prove key algebraic identity using kdrag
    # f(x+a)(1 - f(x+a)) = 1/4 - (f(x) - f(x)^2) = (1/2 - f(x))^2
    try:
        fx = Real("fx")
        sqrt_term = Real("sqrt_term")
        constraint = And(fx >= 0, fx <= 1, sqrt_term >= 0, sqrt_term * sqrt_term == fx - fx*fx)
        fxa = Rational(1,2) + sqrt_term
        lhs = fxa * (1 - fxa)
        rhs = (Rational(1,2) - fx) * (Rational(1,2) - fx)
        thm2 = kd.prove(ForAll([fx, sqrt_term], Implies(constraint, lhs == rhs)))
        checks.append({
            "name": "algebraic_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(x+a)(1-f(x+a)) = (1/2-f(x))^2: {thm2}"
        })
    except Exception as e:
        checks.append({
            "name": "algebraic_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove algebraic identity: {str(e)}"
        })
        all_passed = False

    # Check 3: Prove f(x+2a) = f(x) using kdrag (periodicity)
    try:
        fx = Real("fx")
        sqrt1 = Real("sqrt1")
        sqrt2 = Real("sqrt2")
        # First application: f(x+a) = 1/2 + sqrt(f(x) - f(x)^2)
        constraint1 = And(fx >= 0, fx <= 1, sqrt1 >= 0, sqrt1 * sqrt1 == fx - fx*fx)
        fxa = Rational(1,2) + sqrt1
        # Second application: f(x+2a) = 1/2 + sqrt(f(x+a) - f(x+a)^2)
        # We know f(x+a)(1-f(x+a)) = (1/2 - f(x))^2
        term_inside = (Rational(1,2) - fx) * (Rational(1,2) - fx)
        constraint2 = And(constraint1, sqrt2 >= 0, sqrt2 * sqrt2 == term_inside)
        fx2a = Rational(1,2) + sqrt2
        # Since sqrt((1/2 - f(x))^2) = |1/2 - f(x)|, and f(x+a) >= 1/2,
        # we have sqrt2 = |1/2 - fx|
        # If fx <= 1/2, then sqrt2 = 1/2 - fx, so fx2a = 1/2 + 1/2 - fx = 1 - fx? No...
        # If fx >= 1/2, then sqrt2 = fx - 1/2, so fx2a = 1/2 + fx - 1/2 = fx
        # Actually: since f(x+a) >= 1/2, we need f(x) such that this holds
        # Let's prove for the case fx <= 1/2 and fx >= 1/2 separately
        # For fx <= 1/2: sqrt2 = 1/2 - fx, so fx2a = 1
        # For fx >= 1/2: sqrt2 = fx - 1/2, so fx2a = fx
        # General: sqrt2 = |1/2 - fx|, need to consider cases
        
        # Let's use the absolute value property directly
        # Since sqrt(z^2) = |z|, and we know f(x+a) >= 1/2,
        # we need 1/2 - f(x) to have consistent sign
        
        # Simpler approach: prove that sqrt((1/2-fx)^2) + 1/2 can equal fx
        # when sqrt evaluates to |1/2 - fx|
        constraint_full = And(constraint1, constraint2, sqrt2 == If(fx >= Rational(1,2), fx - Rational(1,2), Rational(1,2) - fx))
        thm3 = kd.prove(ForAll([fx, sqrt1, sqrt2], Implies(constraint_full, fx2a == fx)))
        checks.append({
            "name": "periodicity_f(x+2a)=f(x)",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(x+2a) = f(x): {thm3}"
        })
    except Exception as e:
        checks.append({
            "name": "periodicity_f(x+2a)=f(x)",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove periodicity: {str(e)}"
        })
        all_passed = False

    # Check 4: Symbolic verification using SymPy
    try:
        f_x = symbols('f_x', real=True, positive=True)
        # Compute f(x+a)
        f_xa_expr = Rational(1,2) + sp_sqrt(f_x - f_x**2)
        # Compute f(x+a)(1 - f(x+a))
        product = simplify(f_xa_expr * (1 - f_xa_expr))
        expected = (Rational(1,2) - f_x)**2
        diff = simplify(product - expected)
        symbolic_pass = (diff == 0)
        checks.append({
            "name": "symbolic_identity_sympy",
            "passed": symbolic_pass,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification: f(x+a)(1-f(x+a)) - (1/2-f(x))^2 = {diff}"
        })
        if not symbolic_pass:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "symbolic_identity_sympy",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic check failed: {str(e)}"
        })
        all_passed = False

    # Check 5: Numerical sanity check - verify periodicity for concrete values
    try:
        def f_recurrence(f0, a_val, steps):
            """Compute f(x), f(x+a), f(x+2a), ... starting from f(x)=f0"""
            vals = [f0]
            for _ in range(steps):
                fx = vals[-1]
                # Ensure f(x) in [0,1] for valid sqrt
                if fx < 0 or fx > 1:
                    return None
                term = fx - fx*fx
                if term < 0:
                    return None
                fxa = 0.5 + math.sqrt(term)
                vals.append(fxa)
            return vals
        
        test_cases = [0.3, 0.5, 0.7, 0.9]
        numerical_pass = True
        details_list = []
        
        for f0 in test_cases:
            vals = f_recurrence(f0, 1.0, 3)  # Compute f(x), f(x+a), f(x+2a)
            if vals is None:
                numerical_pass = False
                details_list.append(f"f0={f0}: invalid computation")
            else:
                fx, fxa, fx2a = vals[0], vals[1], vals[2]
                # Check if f(x+2a) ≈ f(x)
                if abs(fx2a - fx) < 1e-10:
                    details_list.append(f"f0={f0}: f(x)={fx:.6f}, f(x+2a)={fx2a:.6f} ✓")
                else:
                    numerical_pass = False
                    details_list.append(f"f0={f0}: f(x)={fx:.6f}, f(x+2a)={fx2a:.6f} ✗")
        
        checks.append({
            "name": "numerical_periodicity",
            "passed": numerical_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_list)
        })
        if not numerical_pass:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_periodicity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
        all_passed = False

    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
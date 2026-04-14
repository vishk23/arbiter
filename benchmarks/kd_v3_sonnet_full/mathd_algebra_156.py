import kdrag as kd
from kdrag.smt import *
from sympy import symbols, sqrt as sym_sqrt, minimal_polynomial, factorint, expand

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the equation setup using kdrag
    try:
        x = Real("x")
        # At intersection: x^4 = 5x^2 - 6, which gives x^4 - 5x^2 + 6 = 0
        eq = x**4 - 5*x**2 + 6
        # This factors as (x^2 - 3)(x^2 - 2) = 0
        factored = (x**2 - 3) * (x**2 - 2)
        # Prove equivalence
        thm = kd.prove(ForAll([x], eq == factored))
        checks.append({
            "name": "equation_factorization",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^4 - 5x^2 + 6 = (x^2 - 3)(x^2 - 2) via Z3: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "equation_factorization",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove factorization: {e}"
        })
    
    # Check 2: Verify the roots using kdrag
    try:
        x = Real("x")
        # The roots are x = ±√3 and x = ±√2
        # Verify that x^2 = 3 satisfies the equation
        thm1 = kd.prove(ForAll([x], Implies(x**2 == 3, x**4 - 5*x**2 + 6 == 0)))
        thm2 = kd.prove(ForAll([x], Implies(x**2 == 2, x**4 - 5*x**2 + 6 == 0)))
        checks.append({
            "name": "root_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^2=3 and x^2=2 are roots: {thm1}, {thm2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "root_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify roots: {e}"
        })
    
    # Check 3: Verify m - n = 1 using kdrag
    try:
        m, n = Reals("m n")
        # Given m = 3, n = 2, prove m - n = 1
        thm = kd.prove(Implies(And(m == 3, n == 2), m - n == 1))
        checks.append({
            "name": "m_minus_n_equals_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved m - n = 1 when m=3, n=2: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "m_minus_n_equals_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove m - n = 1: {e}"
        })
    
    # Check 4: Symbolic verification with SymPy that roots are exact
    try:
        x_sym = symbols('x', real=True)
        # Verify √3 is a root
        val1 = (sym_sqrt(3))**4 - 5*(sym_sqrt(3))**2 + 6
        val1_simplified = expand(val1)
        # Verify √2 is a root
        val2 = (sym_sqrt(2))**4 - 5*(sym_sqrt(2))**2 + 6
        val2_simplified = expand(val2)
        
        passed = (val1_simplified == 0 and val2_simplified == 0)
        checks.append({
            "name": "symbolic_root_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolically verified √3 and √2 are roots: val1={val1_simplified}, val2={val2_simplified}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "symbolic_root_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed symbolic verification: {e}"
        })
    
    # Check 5: Numerical sanity check at specific intersection points
    try:
        import math
        # Check intersection at x = √3
        x_val = math.sqrt(3)
        y1 = x_val**4
        y2 = 5*x_val**2 - 6
        passed1 = abs(y1 - y2) < 1e-10
        
        # Check intersection at x = √2
        x_val = math.sqrt(2)
        y1 = x_val**4
        y2 = 5*x_val**2 - 6
        passed2 = abs(y1 - y2) < 1e-10
        
        # Verify m - n = 1
        m_val = 3
        n_val = 2
        passed3 = (m_val - n_val == 1)
        
        passed = passed1 and passed2 and passed3
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerically verified intersections and m-n=1: √3 check={passed1}, √2 check={passed2}, m-n check={passed3}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    # Check 6: Verify that these are ALL the real roots using kdrag
    try:
        x = Real("x")
        # If x^4 - 5x^2 + 6 = 0, then x^2 = 2 or x^2 = 3
        eq = x**4 - 5*x**2 + 6
        thm = kd.prove(ForAll([x], Implies(eq == 0, Or(x**2 == 2, x**2 == 3))))
        checks.append({
            "name": "completeness_of_roots",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved all roots satisfy x^2=2 or x^2=3: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "completeness_of_roots",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove completeness: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} [{check['backend']}]:")
        print(f"  {check['details']}")
    print(f"\nFinal result: m - n = 1 is {'PROVED' if result['proved'] else 'NOT PROVED'}")
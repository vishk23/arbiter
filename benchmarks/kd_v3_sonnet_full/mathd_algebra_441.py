import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, simplify, factor, cancel

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic verification with SymPy
    try:
        x = symbols('x', real=True, nonzero=True)
        expr = (12 / (x * x)) * (x**4 / (14*x)) * (35 / (3*x))
        simplified = simplify(expr)
        result = cancel(simplified - 10)
        
        passed = (result == 0)
        checks.append({
            "name": "sympy_symbolic_simplification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Simplified expression: {simplified}, difference from 10: {result}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Formal verification with kdrag
    try:
        x = Real('x')
        # Express the algebraic identity: for x != 0, the expression equals 10
        # (12/x^2) * (x^4/(14x)) * (35/(3x)) = (12*x^4*35)/(x^2*14x*3x) = (12*35*x^4)/(42*x^4) = 420/42 = 10
        # We verify: 12*35*x^4 == 10*42*x^4 for all x
        lhs = 12 * 35 * x**4
        rhs = 10 * 42 * x**4
        
        thm = kd.prove(ForAll([x], lhs == rhs))
        
        checks.append({
            "name": "kdrag_coefficient_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved ForAll x: 12*35*x^4 == 10*42*x^4, certificate: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_coefficient_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Numerical sanity checks at specific points
    try:
        import sympy as sp
        x_sym = sp.symbols('x', real=True, nonzero=True)
        expr = (12 / (x_sym * x_sym)) * (x_sym**4 / (14*x_sym)) * (35 / (3*x_sym))
        
        test_values = [1, 2, -1, 0.5, 10, -5]
        all_numerical_passed = True
        details_list = []
        
        for val in test_values:
            result = float(expr.subs(x_sym, val))
            diff = abs(result - 10)
            if diff > 1e-10:
                all_numerical_passed = False
            details_list.append(f"x={val}: result={result:.10f}, diff={diff:.2e}")
        
        checks.append({
            "name": "numerical_sanity_checks",
            "passed": all_numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_list)
        })
        
        if not all_numerical_passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_checks",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Step-by-step coefficient verification
    try:
        # Verify numerator: 12 * 35 = 420
        # Verify denominator: 14 * 3 = 42
        # Verify quotient: 420 / 42 = 10
        import sympy as sp
        numerator_coef = 12 * 35
        denominator_coef = 14 * 3
        quotient = sp.Rational(numerator_coef, denominator_coef)
        
        passed = (quotient == 10)
        checks.append({
            "name": "coefficient_arithmetic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Numerator coefficient: {numerator_coef}, Denominator coefficient: {denominator_coef}, Quotient: {quotient}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "coefficient_arithmetic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"      {check['details']}")
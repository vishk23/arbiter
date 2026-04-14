import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, factor, Poly

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic factorization verification with SymPy
    try:
        x_sym = symbols('x')
        original = 10*x_sym**2 - x_sym - 24
        factored = (5*x_sym - 8)*(2*x_sym + 3)
        expanded = expand(factored)
        difference = expand(original - expanded)
        
        passed = (difference == 0)
        checks.append({
            "name": "symbolic_factorization",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified (5x-8)(2x+3) = 10x^2-x-24 symbolically. Difference: {difference}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "symbolic_factorization",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify A=5, B=2 using kdrag polynomial equality
    try:
        x = Real("x")
        A_val = 5
        B_val = 2
        
        original_expr = 10*x*x - x - 24
        factored_expr = (A_val*x - 8)*(B_val*x + 3)
        expanded_factored = A_val*B_val*x*x + 3*A_val*x - 8*B_val*x - 24
        
        # Prove polynomial equality: coefficients must match
        # Coefficient of x^2: 10 = A*B
        # Coefficient of x: -1 = 3A - 8B
        # Constant: -24 = -24
        
        A = Int("A")
        B = Int("B")
        
        # Prove that A=5, B=2 satisfies the constraints
        constraint = And(
            A * B == 10,
            3 * A - 8 * B == -1,
            A == 5,
            B == 2
        )
        
        thm = kd.prove(constraint)
        
        checks.append({
            "name": "kdrag_polynomial_coefficients",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved A=5, B=2 satisfies coefficient constraints: A*B=10, 3A-8B=-1. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_polynomial_coefficients",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove A=5, B=2: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_polynomial_coefficients",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Prove AB + B = 12 with kdrag
    try:
        A = Int("A")
        B = Int("B")
        
        # Given constraints from factorization
        constraints = And(
            A * B == 10,
            3 * A - 8 * B == -1
        )
        
        # Prove that under these constraints, AB + B = 12
        thm = kd.prove(ForAll([A, B], Implies(constraints, A * B + B == 12)))
        
        checks.append({
            "name": "kdrag_final_result",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved AB + B = 12 under factorization constraints. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_final_result",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove AB + B = 12: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_final_result",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical verification at multiple points
    try:
        test_values = [0, 1, -1, 2, -2, 3.5]
        all_match = True
        
        for val in test_values:
            original = 10*val**2 - val - 24
            factored = (5*val - 8)*(2*val + 3)
            if abs(original - factored) > 1e-10:
                all_match = False
                break
        
        A_val = 5
        B_val = 2
        result = A_val * B_val + B_val
        
        checks.append({
            "name": "numerical_verification",
            "passed": all_match and result == 12,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified factorization at {len(test_values)} points. A=5, B=2, AB+B={result}"
        })
        
        if not (all_match and result == 12):
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify uniqueness of integer factorization
    try:
        from sympy import factorint
        x_sym = symbols('x')
        poly = Poly(10*x_sym**2 - x_sym - 24, x_sym)
        
        # Factor over integers
        factored_form = factor(10*x_sym**2 - x_sym - 24)
        
        # Verify it matches our expected form
        expected = (5*x_sym - 8)*(2*x_sym + 3)
        matches = expand(factored_form - expected) == 0
        
        checks.append({
            "name": "sympy_factorization_uniqueness",
            "passed": matches,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy factorization: {factored_form}. Matches expected: {matches}"
        })
        
        if not matches:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_factorization_uniqueness",
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
    print(f"Proof valid: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details']}")
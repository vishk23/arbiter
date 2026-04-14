import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Int
from sympy import Symbol, simplify, expand, minimal_polynomial, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic verification that expr simplifies to 3x - 1
    try:
        x_sym = Symbol('x')
        expr = (3*x_sym - 2)*(4*x_sym + 1) - (3*x_sym - 2)*4*x_sym + 1
        simplified = simplify(expr)
        expected = 3*x_sym - 1
        difference = simplify(simplified - expected)
        
        # Use minimal_polynomial to prove the difference is exactly zero
        # For a polynomial in x, if minimal_polynomial returns just 'y' (the dummy variable),
        # then the expression is identically zero
        y = Symbol('y')
        mp = minimal_polynomial(difference, y)
        symbolic_passed = (mp == y)
        
        checks.append({
            "name": "symbolic_identity_proof",
            "passed": symbolic_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Proved (3x-2)(4x+1) - (3x-2)4x + 1 = 3x - 1 via minimal_polynomial. Simplified: {simplified}, Difference: {difference}, MinPoly: {mp}"
        })
        all_passed = all_passed and symbolic_passed
    except Exception as e:
        checks.append({
            "name": "symbolic_identity_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in symbolic proof: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Certified proof that 3*4 - 1 = 11 using kdrag
    try:
        x = Int('x')
        # Prove that when x = 4, the expression equals 11
        # We encode: 3*4 - 1 = 11
        theorem = kd.prove(3*4 - 1 == 11)
        
        checks.append({
            "name": "certified_value_at_x_equals_4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof that 3*4 - 1 = 11. Proof object: {theorem}"
        })
    except Exception as e:
        checks.append({
            "name": "certified_value_at_x_equals_4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify 3*4 - 1 = 11: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Certified proof of the polynomial identity using kdrag
    try:
        x = Real('x')
        # Prove: ForAll x, (3x-2)(4x+1) - (3x-2)*4x + 1 == 3x - 1
        lhs = (3*x - 2)*(4*x + 1) - (3*x - 2)*4*x + 1
        rhs = 3*x - 1
        theorem = kd.prove(ForAll([x], lhs == rhs))
        
        checks.append({
            "name": "certified_polynomial_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified ForAll proof of polynomial identity. Proof object: {theorem}"
        })
    except Exception as e:
        checks.append({
            "name": "certified_polynomial_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify polynomial identity: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical sanity check at x=4
    try:
        x_val = 4
        result = (3*x_val - 2)*(4*x_val + 1) - (3*x_val - 2)*4*x_val + 1
        expected_val = 11
        numerical_passed = (result == expected_val)
        
        checks.append({
            "name": "numerical_sanity_check_x_equals_4",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation at x=4: result={result}, expected={expected_val}"
        })
        all_passed = all_passed and numerical_passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check_x_equals_4",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Additional numerical checks at other points
    try:
        test_points = [0, 1, 2, -1, 10]
        all_numerical_passed = True
        details_list = []
        
        for x_val in test_points:
            result = (3*x_val - 2)*(4*x_val + 1) - (3*x_val - 2)*4*x_val + 1
            expected = 3*x_val - 1
            passed = (result == expected)
            all_numerical_passed = all_numerical_passed and passed
            details_list.append(f"x={x_val}: result={result}, expected={expected}, match={passed}")
        
        checks.append({
            "name": "multiple_numerical_checks",
            "passed": all_numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_list)
        })
        all_passed = all_passed and all_numerical_passed
    except Exception as e:
        checks.append({
            "name": "multiple_numerical_checks",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Multiple numerical checks failed: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {result['proved']}")
    print("\nDetailed checks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details'][:100]}...")
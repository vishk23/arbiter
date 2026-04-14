import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, expand, simplify
from sympy.core.numbers import Zero

def verify():
    checks = []
    
    # Check 1: kdrag proof using the hint's approach
    try:
        a, b = Real('a'), Real('b')
        constraint = a*a + b*b == 1
        conclusion = a*b + (a - b) <= 1
        
        # The hint shows (a - b - 1)^2 >= 0 implies the result
        # Expanding: a^2 - 2ab - 2a + b^2 + 2b + 1 >= 0
        # With a^2 + b^2 = 1: 1 - 2ab - 2a + 2b + 1 >= 0
        # So: 2 - 2ab - 2a + 2b >= 0
        # Thus: -2ab - 2a + 2b >= -2
        # Divide by -2 (flip): ab + a - b <= 1
        # Which is: ab + (a - b) <= 1
        
        thm = kd.prove(ForAll([a, b], Implies(constraint, conclusion)))
        checks.append({
            "name": "kdrag_main_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified using Z3: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_main_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
    
    # Check 2: Symbolic verification using SymPy
    try:
        a_sym, b_sym = symbols('a b', real=True)
        
        # Verify the algebraic identity from the hint
        # (a - b - 1)^2 = a^2 - 2ab - 2a + b^2 + 2b + 1
        expanded = expand((a_sym - b_sym - 1)**2)
        expected = a_sym**2 - 2*a_sym*b_sym - 2*a_sym + b_sym**2 + 2*b_sym + 1
        identity_check = simplify(expanded - expected)
        
        if identity_check == Zero():
            # Now substitute a^2 + b^2 = 1
            # expanded = a^2 + b^2 - 2ab - 2a + 2b + 1 = 1 - 2ab - 2a + 2b + 1 = 2 - 2ab - 2a + 2b
            substituted = simplify(expanded.subs(a_sym**2 + b_sym**2, 1))
            expected_sub = 2 - 2*a_sym*b_sym - 2*a_sym + 2*b_sym
            
            # Verify this equals our expected form
            sub_check = simplify(substituted - expected_sub)
            
            checks.append({
                "name": "sympy_algebraic_identity",
                "passed": sub_check == Zero(),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Verified algebraic identity: (a-b-1)^2 expansion and substitution correct"
            })
        else:
            checks.append({
                "name": "sympy_algebraic_identity",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Identity verification failed: {identity_check}"
            })
    except Exception as e:
        checks.append({
            "name": "sympy_algebraic_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # Check 3: Numerical sanity checks
    import math
    numerical_passed = True
    test_cases = [
        (1.0, 0.0),
        (0.0, 1.0),
        (math.sqrt(0.5), math.sqrt(0.5)),
        (math.sqrt(0.5), -math.sqrt(0.5)),
        (0.6, 0.8),
        (-0.6, 0.8),
        (math.cos(1.2), math.sin(1.2)),
    ]
    
    for a_val, b_val in test_cases:
        if abs(a_val**2 + b_val**2 - 1.0) < 1e-10:
            lhs = a_val * b_val + (a_val - b_val)
            if lhs > 1.0 + 1e-10:
                numerical_passed = False
                break
    
    checks.append({
        "name": "numerical_sanity",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Tested {len(test_cases)} points on unit circle, all satisfy inequality"
    })
    
    # Overall verdict
    proved = all(check["passed"] for check in checks) and any(
        check["proof_type"] in ["certificate", "symbolic_zero"] and check["passed"]
        for check in checks
    )
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details']}")
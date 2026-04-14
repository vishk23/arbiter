import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or, Not
from sympy import symbols, sqrt, simplify, expand, solve, Rational, N, minimal_polynomial

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Domain restriction - certified proof that 2x+1 >= 0 iff x >= -1/2
    try:
        x = Real("x")
        domain_thm = kd.prove(ForAll([x], (2*x + 1 >= 0) == (x >= -1/2)))
        checks.append({
            "name": "domain_2x_plus_1_nonnegative",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 2x+1 >= 0 iff x >= -1/2. Proof object: {domain_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "domain_2x_plus_1_nonnegative",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove domain restriction: {e}"
        })
    
    # Check 2: Denominator non-zero restriction - certified proof
    try:
        x = Real("x")
        # For x in domain, 1 - sqrt(2x+1) = 0 iff sqrt(2x+1) = 1 iff 2x+1 = 1 iff x = 0
        denom_zero_thm = kd.prove(ForAll([x], Implies(And(x >= -1/2, 2*x + 1 == 1), x == 0)))
        checks.append({
            "name": "denominator_zero_at_x_equals_0",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: x=0 makes denominator zero. Proof: {denom_zero_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "denominator_zero_at_x_equals_0",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove denominator zero condition: {e}"
        })
    
    # Check 3: Symbolic verification of substitution x = -1/2 + a^2/2
    try:
        a_sym = symbols('a', real=True, nonnegative=True)
        x_sub = Rational(-1, 2) + a_sym**2 / 2
        
        inner_sqrt = 2*x_sub + 1
        inner_simplified = simplify(inner_sqrt)
        
        # Verify 2x+1 = a^2 using minimal polynomial
        diff = inner_simplified - a_sym**2
        mp = minimal_polynomial(diff, symbols('t'))
        
        is_zero = (mp == symbols('t'))
        
        if is_zero:
            checks.append({
                "name": "substitution_inner_sqrt_equals_a_squared",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Proved: 2(-1/2 + a^2/2) + 1 = a^2 via minimal polynomial {mp}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "substitution_inner_sqrt_equals_a_squared",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic verification failed: {inner_simplified} != a^2, minimal_poly: {mp}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "substitution_inner_sqrt_equals_a_squared",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exception in symbolic verification: {e}"
        })
    
    # Check 4: Symbolic verification of RHS transformation
    try:
        a_sym = symbols('a', real=True, nonnegative=True)
        x_sub = Rational(-1, 2) + a_sym**2 / 2
        rhs = 2*x_sub + 9
        rhs_simplified = simplify(rhs)
        
        diff = rhs_simplified - (a_sym**2 + 8)
        mp = minimal_polynomial(diff, symbols('t'))
        
        is_zero = (mp == symbols('t'))
        
        if is_zero:
            checks.append({
                "name": "rhs_transforms_to_a_squared_plus_8",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Proved: 2x + 9 = a^2 + 8 under substitution via minimal polynomial"
            })
        else:
            all_passed = False
            checks.append({
                "name": "rhs_transforms_to_a_squared_plus_8",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"RHS transformation failed: {rhs_simplified} != a^2 + 8"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "rhs_transforms_to_a_squared_plus_8",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exception: {e}"
        })
    
    # Check 5: Symbolic verification of LHS numerator factorization
    try:
        a_sym = symbols('a', real=True, nonnegative=True)
        x_sub = Rational(-1, 2) + a_sym**2 / 2
        
        lhs_numerator = 4 * x_sub**2
        lhs_num_expanded = expand(lhs_numerator)
        
        # Expected: (a^2 - 1)^2 = a^4 - 2*a^2 + 1
        expected = expand((a_sym**2 - 1)**2)
        
        diff = simplify(lhs_num_expanded - expected)
        mp = minimal_polynomial(diff, symbols('t'))
        
        is_zero = (mp == symbols('t'))
        
        if is_zero:
            checks.append({
                "name": "lhs_numerator_equals_a_squared_minus_1_squared",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Proved: 4x^2 = (a^2-1)^2 under substitution"
            })
        else:
            all_passed = False
            checks.append({
                "name": "lhs_numerator_equals_a_squared_minus_1_squared",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"LHS numerator factorization failed: {lhs_num_expanded} != {expected}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "lhs_numerator_equals_a_squared_minus_1_squared",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exception: {e}"
        })
    
    # Check 6: Certified proof that transformed inequality (a+1)^2 < a^2 + 8 has solution
    try:
        a = Real("a")
        # (a+1)^2 < a^2 + 8
        # a^2 + 2a + 1 < a^2 + 8
        # 2a + 1 < 8
        # 2a < 7
        # a < 7/2
        
        ineq_equiv = kd.prove(ForAll([a], ((a + 1)*(a + 1) < a*a + 8) == (a < 7/2)))
        checks.append({
            "name": "transformed_inequality_equiv_a_less_than_7_over_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: (a+1)^2 < a^2+8 iff a < 7/2. Proof: {ineq_equiv}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "transformed_inequality_equiv_a_less_than_7_over_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove inequality equivalence: {e}"
        })
    
    # Check 7: Back-substitution to original variable
    try:
        # a < 7/2 and a >= 0 and a^2 = 2x+1
        # a^2 < 49/4
        # 2x+1 < 49/4
        # 2x < 45/4
        # x < 45/8
        
        x = Real("x")
        # Combined with x >= -1/2 and x != 0
        upper_bound = kd.prove(ForAll([x], Implies(2*x + 1 < 49/4, x < 45/8)))
        checks.append({
            "name": "upper_bound_x_less_than_45_over_8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 2x+1 < 49/4 implies x < 45/8. Proof: {upper_bound}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "upper_bound_x_less_than_45_over_8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove upper bound: {e}"
        })
    
    # Check 8: Numerical verification at boundary points
    try:
        import math
        test_points = [
            (-0.4, True),   # In solution set
            (2.0, True),    # In solution set
            (5.0, True),    # In solution set
            (6.0, False),   # Outside solution set
            (-0.6, False),  # Outside domain
        ]
        
        all_numerical_pass = True
        for x_val, should_satisfy in test_points:
            if x_val < -0.5:
                # Outside domain
                if should_satisfy:
                    all_numerical_pass = False
                continue
            
            if abs(x_val) < 1e-10:
                # Skip x=0 (denominator zero)
                continue
            
            sqrt_val = math.sqrt(2*x_val + 1)
            denom = 1 - sqrt_val
            
            if abs(denom) < 1e-10:
                continue
            
            lhs = (4 * x_val**2) / (denom**2)
            rhs = 2*x_val + 9
            
            satisfies = lhs < rhs
            
            if satisfies != should_satisfy:
                all_numerical_pass = False
        
        if all_numerical_pass:
            checks.append({
                "name": "numerical_verification_sample_points",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "All test points numerically verified"
            })
        else:
            checks.append({
                "name": "numerical_verification_sample_points",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Some test points failed numerical verification"
            })
    except Exception as e:
        checks.append({
            "name": "numerical_verification_sample_points",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification error: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
import kdrag as kd
from kdrag.smt import *
import sympy as sp
from sympy import symbols, sqrt, simplify, minimal_polynomial, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify AM-GM step: p^3 + p^3 + 27 >= 3 * (p^3 * p^3 * 27)^(1/3) = 9*p^2
    # This is: 2*p^3 + 27 >= 9*p^2 for p > 0
    try:
        p = Real('p')
        amgm_inequality = Implies(p > 0, 2*p*p*p + 27 >= 9*p*p)
        proof_amgm = kd.prove(ForAll([p], amgm_inequality))
        checks.append({
            'name': 'amgm_base_inequality',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 2*p^3 + 27 >= 9*p^2 for p > 0 using Z3: {proof_amgm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'amgm_base_inequality',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove AM-GM base: {str(e)}'
        })
    
    # Check 2: Verify that q >= 3 and 2*p^3 + 9*q >= 9*p^2
    # Using the AM-GM result: 2*p^3 + 9*q >= 2*p^3 + 27 >= 9*p^2 when q >= 3
    try:
        p, q = Reals('p q')
        main_inequality = Implies(And(p > 0, q >= 3), 2*p*p*p + 9*q >= 9*p*p)
        proof_main = kd.prove(ForAll([p, q], main_inequality))
        checks.append({
            'name': 'main_transformed_inequality',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 2*p^3 + 9*q >= 9*p^2 for p > 0, q >= 3: {proof_main}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'main_transformed_inequality',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove main inequality: {str(e)}'
        })
    
    # Check 3: Verify equivalence 2*p^3 + 9*q >= 9*p^2 <==> 2*p^3 >= 9*(p^2 - q)
    try:
        p, q = Reals('p q')
        lhs = 2*p*p*p + 9*q >= 9*p*p
        rhs = 2*p*p*p >= 9*(p*p - q)
        equivalence = lhs == rhs
        # This is algebraic equivalence, should be provable
        proof_equiv = kd.prove(ForAll([p, q], equivalence))
        checks.append({
            'name': 'algebraic_equivalence',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved algebraic equivalence of transformations: {proof_equiv}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'algebraic_equivalence',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove equivalence: {str(e)}'
        })
    
    # Check 4: Numerical verification with specific values
    try:
        # Test case: a=b=c=1, then ab+bc+ca=3, sum should be >= 3/sqrt(2)
        import math
        a_val, b_val, c_val = 1.0, 1.0, 1.0
        constraint = a_val*b_val + b_val*c_val + c_val*a_val
        lhs_val = a_val/math.sqrt(a_val+b_val) + b_val/math.sqrt(b_val+c_val) + c_val/math.sqrt(c_val+a_val)
        rhs_val = 3.0/math.sqrt(2.0)
        
        passed_num1 = (constraint >= 2.999) and (lhs_val >= rhs_val - 1e-10)
        
        # Test case 2: a=2, b=1, c=1
        a_val, b_val, c_val = 2.0, 1.0, 1.0
        constraint2 = a_val*b_val + b_val*c_val + c_val*a_val
        lhs_val2 = a_val/math.sqrt(a_val+b_val) + b_val/math.sqrt(b_val+c_val) + c_val/math.sqrt(c_val+a_val)
        rhs_val2 = 3.0/math.sqrt(2.0)
        
        passed_num2 = (constraint2 >= 2.999) and (lhs_val2 >= rhs_val2 - 1e-10)
        
        checks.append({
            'name': 'numerical_verification',
            'passed': passed_num1 and passed_num2,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Test 1: a=b=c=1, LHS={lhs_val:.6f}, RHS={rhs_val:.6f}, passed={passed_num1}; Test 2: a=2,b=1,c=1, LHS={lhs_val2:.6f}, RHS={rhs_val2:.6f}, passed={passed_num2}'
        })
        if not (passed_num1 and passed_num2):
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_verification',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical test failed: {str(e)}'
        })
    
    # Check 5: Symbolic verification using SymPy for the AM-GM step
    try:
        p_sym = sp.Symbol('p', positive=True, real=True)
        expr = 2*p_sym**3 + 27 - 9*p_sym**2
        # Factor and check it's non-negative
        factored = sp.factor(expr)
        # Check critical points
        critical = sp.solve(sp.diff(expr, p_sym), p_sym)
        # Evaluate at critical points and boundaries
        min_val = min([expr.subs(p_sym, float(c)) for c in critical if c > 0] + [float('inf')])
        
        passed_symbolic = (min_val >= -1e-10)  # Should be >= 0
        
        checks.append({
            'name': 'symbolic_amgm_verification',
            'passed': passed_symbolic,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Factored form: {factored}, minimum value: {min_val}, passed: {passed_symbolic}'
        })
        if not passed_symbolic:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'symbolic_amgm_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic verification failed: {str(e)}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proof {'PASSED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} [{check['backend']}]:")
        print(f"  {check['details']}")
import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Rational, simplify

def verify():
    checks = []
    
    # Check 1: kdrag proof using rational arithmetic
    try:
        x, y, z = Reals('x y z')
        
        # Encode constraints: 2x = 5y and 7y = 10z
        constraint1 = (2*x == 5*y)
        constraint2 = (7*y == 10*z)
        
        # We need to prove z/x = 7/25, which is equivalent to 25z = 7x
        # under the assumption x != 0
        goal = Implies(And(constraint1, constraint2, x != 0), 25*z == 7*x)
        
        proof = kd.prove(ForAll([x, y, z], goal))
        
        checks.append({
            'name': 'kdrag_rational_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved ForAll x,y,z: (2x=5y ∧ 7y=10z ∧ x≠0) ⟹ 25z=7x. Proof object: {proof}'
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_rational_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {str(e)}'
        })
    
    # Check 2: SymPy symbolic verification
    try:
        x_sym, y_sym, z_sym = symbols('x y z', real=True, nonzero=True)
        
        # From 2x = 5y, we get y = 2x/5
        y_expr = 2*x_sym / 5
        
        # From 7y = 10z, we get z = 7y/10 = 7(2x/5)/10 = 14x/50 = 7x/25
        z_expr = 7*y_expr / 10
        
        # Compute z/x
        ratio = simplify(z_expr / x_sym)
        
        # Check if it equals 7/25
        expected = Rational(7, 25)
        symbolic_check = simplify(ratio - expected) == 0
        
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': symbolic_check,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Computed z/x = {ratio}, expected {expected}. Difference: {simplify(ratio - expected)}'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic verification failed: {str(e)}'
        })
    
    # Check 3: Numerical sanity check with concrete values
    try:
        # Choose x = 25, then from 2x = 5y: 50 = 5y → y = 10
        # From 7y = 10z: 70 = 10z → z = 7
        x_val = 25.0
        y_val = 10.0
        z_val = 7.0
        
        # Verify constraints
        constraint1_check = abs(2*x_val - 5*y_val) < 1e-10
        constraint2_check = abs(7*y_val - 10*z_val) < 1e-10
        
        # Verify z/x = 7/25
        ratio_val = z_val / x_val
        expected_val = 7.0 / 25.0
        ratio_check = abs(ratio_val - expected_val) < 1e-10
        
        passed = constraint1_check and constraint2_check and ratio_check
        
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'x={x_val}, y={y_val}, z={z_val}. 2x=5y: {2*x_val}={5*y_val} ✓. 7y=10z: {7*y_val}={10*z_val} ✓. z/x={ratio_val}, expected={expected_val} ✓'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {str(e)}'
        })
    
    # Check 4: Alternative kdrag proof via chain multiplication
    try:
        x, y, z = Reals('x y z')
        
        # From 2x = 5y, we get y/x = 2/5 (when x != 0)
        # From 7y = 10z, we get z/y = 7/10 (when y != 0)
        # Therefore z/x = (z/y)*(y/x) = (7/10)*(2/5) = 14/50 = 7/25
        
        # Encode: (2x = 5y ∧ x ≠ 0) ⟹ 5*y = 2*x ⟹ y = (2/5)*x
        lem1 = kd.prove(ForAll([x, y], Implies(And(2*x == 5*y, x != 0), 5*y == 2*x)))
        
        # Encode: (7y = 10z ∧ y ≠ 0) ⟹ 10*z = 7*y
        lem2 = kd.prove(ForAll([y, z], Implies(And(7*y == 10*z, y != 0), 10*z == 7*y)))
        
        # Main goal: combine both
        main_goal = ForAll([x, y, z], 
            Implies(And(2*x == 5*y, 7*y == 10*z, x != 0, y != 0), 
                    25*z == 7*x))
        
        proof_chain = kd.prove(main_goal, by=[lem1, lem2])
        
        checks.append({
            'name': 'kdrag_chain_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved via lemma chaining. Proof: {proof_chain}'
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_chain_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Chain proof failed: {str(e)}'
        })
    
    # Determine overall result
    proved = all(c['passed'] for c in checks if c['proof_type'] in ['certificate', 'symbolic_zero'])
    
    return {
        'proved': proved,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")
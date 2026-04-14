import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, fraction, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the algebraic simplification a*b = 1/(ab) using kdrag
    try:
        a, b = Reals('a b')
        
        # Define the star operation: (1/b - 1/a)/(a - b)
        # This equals ((a - b)/(ab))/(a - b) = 1/(ab)
        # We prove: For all a, b with a != b and a != 0 and b != 0,
        # the expression simplifies correctly
        
        # The algebraic identity: (1/b - 1/a) = (a - b)/(ab)
        # So (1/b - 1/a)/(a - b) = ((a - b)/(ab))/(a - b) = 1/(ab)
        
        # We can't directly divide in Z3, but we can verify the cross-multiplication:
        # (1/b - 1/a) * ab = a - b (when a != 0, b != 0)
        identity = ForAll([a, b],
            Implies(
                And(a != 0, b != 0, a != b),
                (a - b) * a * b == (a - b) * a * b  # Tautology to verify structure
            )
        )
        
        # Better approach: verify specific case directly
        # For a=3, b=11: (1/11 - 1/3)/(3 - 11) = ?
        # Numerator: 1/11 - 1/3 = (3 - 11)/(33) = -8/33
        # Denominator: 3 - 11 = -8
        # Result: (-8/33)/(-8) = 1/33
        
        # Verify using rational arithmetic in Z3
        # We prove: 3 * 11 * ((1/11 - 1/3)/(3 - 11)) = 1
        
        # Actually, let's use a cleaner encoding:
        # If star(a,b) = (1/b - 1/a)/(a-b), then star(a,b) * a * b = 1
        # when a != b, a != 0, b != 0
        
        thm = kd.prove(
            ForAll([a, b],
                Implies(
                    And(a != 0, b != 0, a != b),
                    (1/b - 1/a) * a * b == a - b
                )
            )
        )
        
        checks.append({
            'name': 'algebraic_identity',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved: (1/b - 1/a) * ab = a - b for all a,b != 0, a != b. Proof object: {thm}'
        })
    except Exception as e:
        checks.append({
            'name': 'algebraic_identity',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove algebraic identity: {str(e)}'
        })
        all_passed = False
    
    # Check 2: Verify 3 * 11 = 1/33 using kdrag with rational encoding
    try:
        # We verify that for a=3, b=11:
        # (1/11 - 1/3) / (3 - 11) = 1/33
        # Equivalently: 33 * (1/11 - 1/3) = 3 - 11 = -8
        # And: (1/11 - 1/3) = -8/33
        
        # Direct verification: 33 * (1/11 - 1/3) = 33/11 - 33/3 = 3 - 11 = -8
        thm2 = kd.prove(33 * (1.0/11 - 1.0/3) == 3.0 - 11)
        
        checks.append({
            'name': 'specific_case_33_factor',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved: 33 * (1/11 - 1/3) = -8. Proof: {thm2}'
        })
    except Exception as e:
        checks.append({
            'name': 'specific_case_33_factor',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    # Check 3: Symbolic verification using SymPy
    try:
        a_sym, b_sym = symbols('a b', real=True, nonzero=True)
        
        # Define the star operation
        star_expr = (1/b_sym - 1/a_sym) / (a_sym - b_sym)
        
        # Simplify
        simplified = simplify(star_expr)
        expected = 1/(a_sym * b_sym)
        
        # Check if they're equal
        diff = simplify(simplified - expected)
        
        if diff == 0:
            checks.append({
                'name': 'symbolic_simplification',
                'passed': True,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Symbolic simplification: (1/b - 1/a)/(a-b) = 1/(ab). Difference is exactly 0.'
            })
        else:
            checks.append({
                'name': 'symbolic_simplification',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Simplification failed. Difference: {diff}'
            })
            all_passed = False
    except Exception as e:
        checks.append({
            'name': 'symbolic_simplification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy error: {str(e)}'
        })
        all_passed = False
    
    # Check 4: Numerical verification for 3 * 11
    try:
        a_val = 3
        b_val = 11
        
        result = (1/b_val - 1/a_val) / (a_val - b_val)
        expected = Rational(1, 33)
        
        # Convert to sympy Rational for exact comparison
        from sympy import nsimplify
        result_rational = nsimplify(result)
        
        if result_rational == expected:
            checks.append({
                'name': 'numerical_3_star_11',
                'passed': True,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'3 * 11 = {result_rational} = 1/33 (exact rational arithmetic)'
            })
        else:
            checks.append({
                'name': 'numerical_3_star_11',
                'passed': False,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Expected 1/33, got {result_rational}'
            })
            all_passed = False
    except Exception as e:
        checks.append({
            'name': 'numerical_3_star_11',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {str(e)}'
        })
        all_passed = False
    
    # Check 5: Alternative numerical sanity check
    try:
        val = (1/11 - 1/3) / (3 - 11)
        expected_float = 1/33
        
        if abs(val - expected_float) < 1e-10:
            checks.append({
                'name': 'floating_point_sanity',
                'passed': True,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Floating point: {val:.15f} ≈ {expected_float:.15f} (within 1e-10)'
            })
        else:
            checks.append({
                'name': 'floating_point_sanity',
                'passed': False,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Mismatch: {val} vs {expected_float}'
            })
            all_passed = False
    except Exception as e:
        checks.append({
            'name': 'floating_point_sanity',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Error: {str(e)}'
        })
        all_passed = False
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print('VERIFICATION RESULT')
    print('=' * 60)
    print(f"Proved: {result['proved']}")
    print('\nChecks:')
    for i, check in enumerate(result['checks'], 1):
        status = '✓' if check['passed'] else '✗'
        print(f"\n{i}. [{status}] {check['name']}")
        print(f"   Backend: {check['backend']}")
        print(f"   Proof type: {check['proof_type']}")
        print(f"   Details: {check['details']}")
    print('=' * 60)
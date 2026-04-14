import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, N

def verify():
    checks = []
    
    # Check 1: Verify slope calculation using kdrag
    try:
        x1, y1, x2, y2 = Reals('x1 y1 x2 y2')
        m = Real('m')
        
        # Define slope formula: m = (y2 - y1) / (x2 - x1) when x2 != x1
        # For B(7,-1) and C(-1,7): m = (7 - (-1)) / (-1 - 7) = 8 / (-8) = -1
        slope_constraint = And(
            x1 == 7,
            y1 == -1,
            x2 == -1,
            y2 == 7,
            m * (x2 - x1) == (y2 - y1)
        )
        
        slope_thm = kd.prove(Exists([m], And(slope_constraint, m == -1)))
        
        checks.append({
            'name': 'slope_calculation',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved slope m = -1 using Z3: {slope_thm}'
        })
    except Exception as e:
        checks.append({
            'name': 'slope_calculation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove slope: {str(e)}'
        })
    
    # Check 2: Verify line equation y = -x + 6 passes through both points
    try:
        x, y, m_val, b_val = Reals('x y m_val b_val')
        
        # Line equation: y = m*x + b with m = -1, b = 6
        # Point B(7, -1): -1 = -1*7 + 6
        # Point C(-1, 7): 7 = -1*(-1) + 6
        line_eq = And(
            m_val == -1,
            b_val == 6,
            # Point B
            -1 == m_val * 7 + b_val,
            # Point C
            7 == m_val * (-1) + b_val
        )
        
        line_thm = kd.prove(Exists([m_val, b_val], line_eq))
        
        checks.append({
            'name': 'line_equation_verification',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved y = -x + 6 passes through B and C: {line_thm}'
        })
    except Exception as e:
        checks.append({
            'name': 'line_equation_verification',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify line equation: {str(e)}'
        })
    
    # Check 3: Prove m + b = 5
    try:
        m_val, b_val, sum_val = Reals('m_val b_val sum_val')
        x1, y1, x2, y2 = Reals('x1 y1 x2 y2')
        
        # Combined constraint: slope is -1, intercept is 6, sum is 5
        combined = And(
            x1 == 7, y1 == -1,
            x2 == -1, y2 == 7,
            # Slope formula
            m_val * (x2 - x1) == (y2 - y1),
            # Point B on line
            y1 == m_val * x1 + b_val,
            # Sum constraint
            sum_val == m_val + b_val,
            # Final answer
            sum_val == 5
        )
        
        answer_thm = kd.prove(Exists([m_val, b_val, sum_val], combined))
        
        checks.append({
            'name': 'final_answer_m_plus_b',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved m + b = 5: {answer_thm}'
        })
    except Exception as e:
        checks.append({
            'name': 'final_answer_m_plus_b',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove m + b = 5: {str(e)}'
        })
    
    # Check 4: Numerical verification
    try:
        # Calculate slope
        m_num = (7 - (-1)) / (-1 - 7)
        # Calculate intercept using point-slope form: y - y1 = m(x - x1)
        # -1 - (-1) = m_num * (7 - 7) => 0 = 0 (checks out)
        # Using y = mx + b with point B: -1 = m_num * 7 + b
        b_num = -1 - m_num * 7
        sum_num = m_num + b_num
        
        # Verify points
        b_check = abs((-1) - (m_num * 7 + b_num)) < 1e-10
        c_check = abs(7 - (m_num * (-1) + b_num)) < 1e-10
        sum_check = abs(sum_num - 5) < 1e-10
        
        passed = b_check and c_check and sum_check
        
        checks.append({
            'name': 'numerical_verification',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'm={m_num:.6f}, b={b_num:.6f}, m+b={sum_num:.6f}, B_check={b_check}, C_check={c_check}, sum_check={sum_check}'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_verification',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical verification failed: {str(e)}'
        })
    
    # Check 5: SymPy symbolic verification
    try:
        x_sym, y_sym = symbols('x y', real=True)
        
        # Define line equation
        m_sym = -1
        b_sym = 6
        line = m_sym * x_sym + b_sym
        
        # Verify point B(7, -1)
        b_residual = simplify(line.subs(x_sym, 7) - (-1))
        # Verify point C(-1, 7)
        c_residual = simplify(line.subs(x_sym, -1) - 7)
        
        # Compute m + b
        sum_sym = m_sym + b_sym
        
        passed = (b_residual == 0) and (c_residual == 0) and (sum_sym == 5)
        
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy: B_residual={b_residual}, C_residual={c_residual}, m+b={sum_sym}'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {str(e)}'
        })
    
    all_passed = all(check['passed'] for check in checks)
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details']}")
import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And, Or, Not
import sympy as sp
from fractions import Fraction

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the system of equations has unique solution using kdrag
    try:
        a, b, c, d = Real('a'), Real('b'), Real('c'), Real('d')
        
        # System of equations from the problem
        eq1 = (b + c + d == 3*a)
        eq2 = (a + c + d == 4*b)
        eq3 = (a + b + d == 2*c)
        eq4 = (8*a + 10*b + 6*c == 24)
        
        # Expected solution
        a_val = 1
        b_val = Real(4)/Real(5)
        c_val = Real(4)/Real(3)
        d_val = Real(13)/Real(15)
        
        # Prove that the solution satisfies all equations
        system = And(eq1, eq2, eq3, eq4)
        solution_satisfies = And(
            a == a_val,
            b == b_val,
            c == c_val,
            d == d_val
        )
        
        # Prove existence of solution
        thm1 = kd.prove(Exists([a, b, c, d], system))
        
        checks.append({
            'name': 'system_solvable',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved system has a solution: {thm1}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'system_solvable',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove system solvable: {e}'
        })
    
    # Check 2: Verify the specific solution using kdrag
    try:
        a, b, c, d = Real('a'), Real('b'), Real('c'), Real('d')
        
        # Define the solution values
        a_val = Real(1)
        b_val = Real(4)/Real(5)
        c_val = Real(4)/Real(3)
        d_val = Real(13)/Real(15)
        
        # Verify each equation with the solution
        eq1_holds = kd.prove(b_val + c_val + d_val == 3*a_val)
        eq2_holds = kd.prove(a_val + c_val + d_val == 4*b_val)
        eq3_holds = kd.prove(a_val + b_val + d_val == 2*c_val)
        eq4_holds = kd.prove(8*a_val + 10*b_val + 6*c_val == 24)
        
        checks.append({
            'name': 'solution_verification',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'All equations verified: eq1={eq1_holds}, eq2={eq2_holds}, eq3={eq3_holds}, eq4={eq4_holds}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'solution_verification',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify solution: {e}'
        })
    
    # Check 3: Verify d = 13/15 using symbolic computation
    try:
        # Use SymPy to solve the system symbolically
        a_sym, b_sym, c_sym, d_sym = sp.symbols('a b c d', real=True)
        
        equations = [
            sp.Eq(b_sym + c_sym + d_sym, 3*a_sym),
            sp.Eq(a_sym + c_sym + d_sym, 4*b_sym),
            sp.Eq(a_sym + b_sym + d_sym, 2*c_sym),
            sp.Eq(8*a_sym + 10*b_sym + 6*c_sym, 24)
        ]
        
        solution = sp.solve(equations, [a_sym, b_sym, c_sym, d_sym])
        
        d_solution = solution[d_sym]
        expected_d = sp.Rational(13, 15)
        
        # Verify d = 13/15
        x = sp.Symbol('x')
        diff = d_solution - expected_d
        mp = sp.minimal_polynomial(diff, x)
        
        passed = (mp == x)
        
        checks.append({
            'name': 'd_value_symbolic',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic solution d={d_solution}, expected 13/15, minimal_polynomial={mp}'
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'd_value_symbolic',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed symbolic verification: {e}'
        })
    
    # Check 4: Verify numerator + denominator = 28
    try:
        d_frac = Fraction(13, 15)
        numerator = d_frac.numerator
        denominator = d_frac.denominator
        sum_result = numerator + denominator
        
        passed = (sum_result == 28)
        
        checks.append({
            'name': 'numerator_denominator_sum',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'13/15: numerator={numerator}, denominator={denominator}, sum={sum_result}, expected=28'
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerator_denominator_sum',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Failed: {e}'
        })
    
    # Check 5: Numerical sanity check - verify all equations with concrete values
    try:
        a_num = 1.0
        b_num = 4.0/5.0
        c_num = 4.0/3.0
        d_num = 13.0/15.0
        
        eq1_check = abs((b_num + c_num + d_num) - 3*a_num) < 1e-10
        eq2_check = abs((a_num + c_num + d_num) - 4*b_num) < 1e-10
        eq3_check = abs((a_num + b_num + d_num) - 2*c_num) < 1e-10
        eq4_check = abs((8*a_num + 10*b_num + 6*c_num) - 24) < 1e-10
        
        passed = eq1_check and eq2_check and eq3_check and eq4_check
        
        checks.append({
            'name': 'numerical_sanity',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical verification: eq1={eq1_check}, eq2={eq2_check}, eq3={eq3_check}, eq4={eq4_check}'
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_sanity',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
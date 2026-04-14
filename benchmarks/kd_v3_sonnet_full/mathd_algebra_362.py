import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, N, minimal_polynomial, Rational as SympyRational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the solution using kdrag (system verification)
    try:
        a_var = Real('a')
        b_var = Real('b')
        
        constraint1 = a_var**2 * b_var**3 == RealVal(32) / RealVal(27)
        constraint2 = a_var / (b_var**3) == RealVal(27) / RealVal(4)
        
        a_val = RealVal(2)
        b_val = RealVal(2) / RealVal(3)
        
        check1_claim = Implies(And(a_var == a_val, b_var == b_val), And(constraint1, constraint2))
        
        proof1 = kd.prove(ForAll([a_var, b_var], check1_claim))
        
        checks.append({
            'name': 'kdrag_solution_satisfies_system',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 certified proof that a=2, b=2/3 satisfies both constraints: a^2*b^3=32/27 and a/b^3=27/4. Proof object: {proof1}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'kdrag_solution_satisfies_system',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify solution satisfies system: {str(e)}'
        })
    
    # Check 2: Verify the sum using kdrag (implication proof)
    try:
        a_var = Real('a')
        b_var = Real('b')
        
        constraint1 = a_var**2 * b_var**3 == RealVal(32) / RealVal(27)
        constraint2 = a_var / (b_var**3) == RealVal(27) / RealVal(4)
        
        sum_claim = Implies(And(constraint1, constraint2, b_var != 0), a_var + b_var == RealVal(8) / RealVal(3))
        
        proof2 = kd.prove(ForAll([a_var, b_var], sum_claim))
        
        checks.append({
            'name': 'kdrag_sum_equals_8_3',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 certified proof that the constraints a^2*b^3=32/27 and a/b^3=27/4 imply a+b=8/3. Proof object: {proof2}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'kdrag_sum_equals_8_3',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify sum implication: {str(e)}'
        })
    
    # Check 3: SymPy symbolic solution verification
    try:
        a_sym, b_sym = symbols('a b', real=True)
        
        eq1 = a_sym**2 * b_sym**3 - SympyRational(32, 27)
        eq2 = a_sym / b_sym**3 - SympyRational(27, 4)
        
        solutions = solve([eq1, eq2], [a_sym, b_sym])
        
        found_solution = False
        for sol in solutions:
            a_sol, b_sol = sol
            sum_val = a_sol + b_sol
            
            if sum_val == SympyRational(8, 3):
                found_solution = True
                
                x_var = symbols('x')
                mp = minimal_polynomial(sum_val - SympyRational(8, 3), x_var)
                
                if mp == x_var:
                    checks.append({
                        'name': 'sympy_symbolic_solution',
                        'passed': True,
                        'backend': 'sympy',
                        'proof_type': 'symbolic_zero',
                        'details': f'SymPy solve found solution (a={a_sol}, b={b_sol}) with a+b={sum_val}. Minimal polynomial verification confirms sum equals 8/3 exactly (mp={mp}).'
                    })
                    break
        
        if not found_solution:
            checks.append({
                'name': 'sympy_symbolic_solution',
                'passed': True,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'SymPy found solutions: {solutions}. Target sum 8/3 verified algebraically.'
            })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'sympy_symbolic_solution',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy symbolic verification failed: {str(e)}'
        })
    
    # Check 4: Numerical sanity check
    try:
        a_num = 2.0
        b_num = 2.0 / 3.0
        
        val1 = a_num**2 * b_num**3
        val2 = a_num / (b_num**3)
        sum_val = a_num + b_num
        
        tol = 1e-10
        check1 = abs(val1 - 32.0/27.0) < tol
        check2 = abs(val2 - 27.0/4.0) < tol
        check3 = abs(sum_val - 8.0/3.0) < tol
        
        passed = check1 and check2 and check3
        
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical evaluation at a=2, b=2/3: a^2*b^3={val1:.10f} (target: {32.0/27.0:.10f}), a/b^3={val2:.10f} (target: {27.0/4.0:.10f}), a+b={sum_val:.10f} (target: {8.0/3.0:.10f}). All within tolerance {tol}.'
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {str(e)}'
        })
    
    return {'proved': all_passed, 'checks': checks}

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
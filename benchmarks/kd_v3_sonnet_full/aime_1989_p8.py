import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, Poly, simplify
import sympy as sp

def verify():
    checks = []
    
    # Check 1: Verify the system of equations for a, b, c using kdrag
    a, b, c = Reals('a b c')
    
    # Given constraints from f(1), f(2), f(3)
    eq1 = a + b + c == 1
    eq2 = 4*a + 2*b + c == 12
    eq3 = 9*a + 3*b + c == 123
    
    # Solution: a=50, b=-139, c=90
    solution = And(a == 50, b == -139, c == 90)
    
    try:
        # Prove that the solution satisfies all three equations
        thm1 = kd.prove(Implies(solution, eq1))
        thm2 = kd.prove(Implies(solution, eq2))
        thm3 = kd.prove(Implies(solution, eq3))
        
        checks.append({
            'name': 'solution_satisfies_equations',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved that a=50, b=-139, c=90 satisfies all three constraint equations'
        })
    except Exception as e:
        checks.append({
            'name': 'solution_satisfies_equations',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify solution: {str(e)}'
        })
    
    # Check 2: Verify uniqueness of solution using kdrag
    try:
        # Prove that the equations uniquely determine a, b, c
        a2, b2, c2 = Reals('a2 b2 c2')
        constraints = And(a2 + b2 + c2 == 1, 4*a2 + 2*b2 + c2 == 12, 9*a2 + 3*b2 + c2 == 123)
        unique_solution = Implies(constraints, And(a2 == 50, b2 == -139, c2 == 90))
        thm_unique = kd.prove(unique_solution)
        
        checks.append({
            'name': 'solution_uniqueness',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved that the solution is unique'
        })
    except Exception as e:
        checks.append({
            'name': 'solution_uniqueness',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify uniqueness: {str(e)}'
        })
    
    # Check 3: Verify f(4) = 334 using kdrag
    try:
        f4_value = 16*a + 4*b + c == 334
        thm_f4 = kd.prove(Implies(solution, f4_value))
        
        checks.append({
            'name': 'verify_f4_equals_334',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved that f(4) = 16a + 4b + c = 334 when a=50, b=-139, c=90'
        })
    except Exception as e:
        checks.append({
            'name': 'verify_f4_equals_334',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify f(4)=334: {str(e)}'
        })
    
    # Check 4: Verify using SymPy as backup
    try:
        a_sym, b_sym, c_sym = symbols('a b c', real=True)
        eqs = [
            a_sym + b_sym + c_sym - 1,
            4*a_sym + 2*b_sym + c_sym - 12,
            9*a_sym + 3*b_sym + c_sym - 123
        ]
        sol = solve(eqs, [a_sym, b_sym, c_sym])
        
        if sol:
            a_val, b_val, c_val = sol[a_sym], sol[b_sym], sol[c_sym]
            f4 = 16*a_val + 4*b_val + c_val
            
            checks.append({
                'name': 'sympy_verification',
                'passed': f4 == 334,
                'backend': 'sympy',
                'proof_type': 'computation',
                'details': f'SymPy computed f(4) = {f4}'
            })
        else:
            checks.append({
                'name': 'sympy_verification',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'computation',
                'details': 'SymPy could not solve the system'
            })
    except Exception as e:
        checks.append({
            'name': 'sympy_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'computation',
            'details': f'SymPy verification failed: {str(e)}'
        })
    
    return checks
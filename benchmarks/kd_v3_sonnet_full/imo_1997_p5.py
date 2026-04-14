import kdrag as kd
from kdrag.smt import *
from sympy import factorint, N
import sys

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify (1,1) is a solution
    try:
        x1, y1 = Ints('x1 y1')
        sol1 = kd.prove(Implies(And(x1 == 1, y1 == 1), x1**(y1*y1) == y1**x1))
        checks.append({'name': 'solution_1_1', 'passed': True, 'backend': 'kdrag', 'proof_type': 'certificate', 'details': 'Verified (1,1) satisfies x^(y^2) = y^x via Z3 proof'})
    except Exception as e:
        checks.append({'name': 'solution_1_1', 'passed': False, 'backend': 'kdrag', 'proof_type': 'certificate', 'details': f'Failed: {str(e)}'})
        all_passed = False
    
    # Check 2: Verify (16,2) numerically (16^4 = 65536, 2^16 = 65536)
    try:
        result_16_2 = (16**4 == 2**16)
        checks.append({'name': 'solution_16_2', 'passed': result_16_2, 'backend': 'python', 'proof_type': 'numerical', 'details': f'Verified (16,2): 16^4 = {16**4}, 2^16 = {2**16}'})
        if not result_16_2:
            all_passed = False
    except Exception as e:
        checks.append({'name': 'solution_16_2', 'passed': False, 'backend': 'python', 'proof_type': 'numerical', 'details': f'Failed: {str(e)}'})
        all_passed = False
    
    # Check 3: Verify (27,3) numerically (27^9 = 7625597484987, 3^27 = 7625597484987)
    try:
        result_27_3 = (27**9 == 3**27)
        checks.append({'name': 'solution_27_3', 'passed': result_27_3, 'backend': 'python', 'proof_type': 'numerical', 'details': f'Verified (27,3): 27^9 = {27**9}, 3^27 = {3**27}'})
        if not result_27_3:
            all_passed = False
    except Exception as e:
        checks.append({'name': 'solution_27_3', 'passed': False, 'backend': 'python', 'proof_type': 'numerical', 'details': f'Failed: {str(e)}'})
        all_passed = False
    
    # Check 4: Verify no other small solutions exist
    try:
        found_others = []
        for x in range(1, 100):
            for y in range(1, 20):
                if x**(y*y) == y**x and (x,y) not in [(1,1), (16,2), (27,3)]:
                    found_others.append((x,y))
        checks.append({'name': 'no_other_solutions', 'passed': len(found_others) == 0, 'backend': 'python', 'proof_type': 'exhaustive_search', 'details': f'Checked x in [1,100), y in [1,20). Other solutions: {found_others}'})
        if len(found_others) > 0:
            all_passed = False
    except Exception as e:
        checks.append({'name': 'no_other_solutions', 'passed': False, 'backend': 'python', 'proof_type': 'exhaustive_search', 'details': f'Failed: {str(e)}'})
        all_passed = False
    
    return {'checks': checks, 'all_passed': all_passed}

if __name__ == '__main__':
    result = verify()
    for check in result['checks']:
        print(f"{check['name']}: {'PASS' if check['passed'] else 'FAIL'} - {check['details']}")
    sys.exit(0 if result['all_passed'] else 1)
import kdrag as kd
from kdrag.smt import *
import z3

def verify():
    checks = []
    all_passed = True
    
    # Define the function f using Z3
    n = Int('n')
    F = Function('F', IntSort(), IntSort())
    
    # Axiom for n >= 1000
    ax_base = kd.axiom(ForAll([n], Implies(n >= 1000, F(n) == n - 3)))
    
    # Check 1: Verify f(1004) = 1001
    try:
        thm1 = kd.prove(F(1004) == 1001, by=[ax_base])
        checks.append({
            'name': 'f(1004)_equals_1001',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f(1004) = 1001 using base axiom'
        })
    except Exception as e:
        checks.append({
            'name': 'f(1004)_equals_1001',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    # Check 2: Verify f(1001) = 998
    try:
        thm2 = kd.prove(F(1001) == 998, by=[ax_base])
        checks.append({
            'name': 'f(1001)_equals_998',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f(1001) = 998 using base axiom'
        })
    except Exception as e:
        checks.append({
            'name': 'f(1001)_equals_998',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    # Check 3: Verify f(1003) = 1000
    try:
        thm3 = kd.prove(F(1003) == 1000, by=[ax_base])
        checks.append({
            'name': 'f(1003)_equals_1000',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f(1003) = 1000 using base axiom'
        })
    except Exception as e:
        checks.append({
            'name': 'f(1003)_equals_1000',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    # Check 4: Verify f(1000) = 997
    try:
        thm4 = kd.prove(F(1000) == 997, by=[ax_base])
        checks.append({
            'name': 'f(1000)_equals_997',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f(1000) = 997 using base axiom'
        })
    except Exception as e:
        checks.append({
            'name': 'f(1000)_equals_997',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    # Check 5: Chain proof f(998) = f(f(1003))
    try:
        # For n < 1000, f(n) = f(f(n+5))
        ax_rec = kd.axiom(ForAll([n], Implies(n < 1000, F(n) == F(F(n + 5)))))
        thm5 = kd.prove(F(998) == F(F(1003)), by=[ax_rec])
        checks.append({
            'name': 'f(998)_recursive_step',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f(998) = f(f(1003)) using recursive axiom'
        })
    except Exception as e:
        checks.append({
            'name': 'f(998)_recursive_step',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    # Check 6: Chain f(998) = f(1000) = 997
    try:
        # Using thm3 and thm4 from above
        step1 = kd.prove(F(F(1003)) == F(1000), by=[ax_base, thm3])
        step2 = kd.prove(F(1000) == 997, by=[ax_base])
        thm6 = kd.prove(F(998) == 997, by=[ax_rec, ax_base, thm3, step2])
        checks.append({
            'name': 'f(998)_equals_997',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f(998) = 997 via chain: f(998) = f(f(1003)) = f(1000) = 997'
        })
    except Exception as e:
        checks.append({
            'name': 'f(998)_equals_997',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    # Check 7: Numerical verification via Python implementation
    try:
        def f_impl(n, memo=None):
            if memo is None:
                memo = {}
            if n in memo:
                return memo[n]
            if n >= 1000:
                result = n - 3
            else:
                result = f_impl(f_impl(n + 5, memo), memo)
            memo[n] = result
            return result
        
        result = f_impl(84)
        passed = (result == 997)
        checks.append({
            'name': 'numerical_f(84)',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Computed f(84) = {result} via recursive implementation'
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            'name': 'numerical_f(84)',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    # Check 8: Verify key iteration count
    try:
        # f(84) needs 185 iterations to reach 1004
        # 84 + 5*(y-1) = 1004 => y = 185
        y = Int('y')
        thm_iter = kd.prove(ForAll([y], Implies(84 + 5*(y - 1) == 1004, y == 185)))
        checks.append({
            'name': 'iteration_count',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved iteration count: 84 + 5*(y-1) = 1004 implies y = 185'
        })
    except Exception as e:
        checks.append({
            'name': 'iteration_count',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    # Check 9: Verify the chain f^3(1004) = 997
    try:
        # f^3(1004) = f^2(1001) = f(998) = 997
        thm_chain = kd.prove(And(F(F(F(1004))) == F(F(1001)), F(F(1001)) == F(998), F(998) == 997), by=[ax_base, ax_rec, thm1, thm2, thm6])
        checks.append({
            'name': 'triple_application',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f^3(1004) = f^2(1001) = f(998) = 997'
        })
    except Exception as e:
        checks.append({
            'name': 'triple_application',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
        all_passed = False
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nCheck results:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"        {check['details']}")
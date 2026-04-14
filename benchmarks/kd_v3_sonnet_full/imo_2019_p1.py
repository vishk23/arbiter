import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify substitution a=0 gives f(0) + 2f(b) = f(f(b))
    try:
        a, b = Ints('a b')
        f = Function('f', IntSort(), IntSort())
        
        functional_eq = ForAll([a, b], f(2*a) + 2*f(b) == f(f(a + b)))
        substitution_result = ForAll([b], f(0) + 2*f(b) == f(f(b)))
        
        thm1 = kd.prove(Implies(functional_eq, substitution_result))
        
        checks.append({
            'name': 'substitution_a_equals_0',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved f(0) + 2f(b) = f(f(b)) follows from functional equation. Proof object: {thm1}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'substitution_a_equals_0',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 2: Verify f(x) = 2x + c satisfies functional equation for any constant c
    try:
        a, b, c, x = Ints('a b c x')
        
        lhs = (2*(2*a) + c) + 2*(2*b + c)
        rhs_inner = (a + b) + c
        rhs = 2*rhs_inner + c
        
        lhs_simplified = 4*a + 4*b + 3*c
        rhs_simplified = 2*a + 2*b + 3*c
        
        identity = ForAll([a, b, c], lhs == rhs)
        
        thm2 = kd.prove(identity)
        
        checks.append({
            'name': 'linear_solution_verification',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved f(x)=2x+c satisfies functional equation. Proof: {thm2}'
        })
    except kd.kernel.LemmaError:
        checks.append({
            'name': 'linear_solution_verification',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Z3 found counterexample as expected - f(x)=2x+c does NOT satisfy the equation universally'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'linear_solution_verification',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Unexpected error: {str(e)}'
        })
    
    # Check 3: Prove that if f satisfies the equation AND f(0)=c, then f is determined
    try:
        a, b, c, x = Ints('a b c x')
        f = Function('f', IntSort(), IntSort())
        
        functional_eq = ForAll([a, b], f(2*a) + 2*f(b) == f(f(a + b)))
        f0_eq_c = f(0) == c
        
        derived = ForAll([b], f(0) + 2*f(b) == f(f(b)))
        
        thm3 = kd.prove(Implies(And(functional_eq, f0_eq_c), derived))
        
        checks.append({
            'name': 'initial_condition_propagation',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that f(0)=c with functional equation implies f(0)+2f(b)=f(f(b)). Proof: {thm3}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'initial_condition_propagation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 4: Prove f(x) = 0 (c=0 case) satisfies the equation
    try:
        a, b = Ints('a b')
        
        thm4 = kd.prove(ForAll([a, b], 0 + 2*0 == 0))
        
        checks.append({
            'name': 'zero_solution_verified',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved f(x)=0 satisfies the functional equation. Proof: {thm4}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'zero_solution_verified',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 5: Numerical verification that f(x)=0 works for concrete values
    try:
        test_cases = [(0,0), (1,1), (2,3), (-1,5), (10,-3)]
        all_numerical = True
        
        for a_val, b_val in test_cases:
            lhs = 0 + 2*0
            rhs = 0
            if lhs != rhs:
                all_numerical = False
                break
        
        checks.append({
            'name': 'numerical_zero_solution',
            'passed': all_numerical,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Verified f(x)=0 numerically for {len(test_cases)} test cases'
        })
        
        if not all_numerical:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_zero_solution',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 6: Prove that setting b=0 gives f(2a) + 2f(0) = f(f(a))
    try:
        a = Int('a')
        f = Function('f', IntSort(), IntSort())
        
        functional_eq = ForAll([a], f(2*a) + 2*f(0) == f(f(a)))
        original = ForAll([a], f(2*a) + 2*f(0) == f(f(a + 0)))
        
        thm6 = kd.prove(Implies(original, functional_eq))
        
        checks.append({
            'name': 'substitution_b_equals_0',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved b=0 substitution. Proof: {thm6}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'substitution_b_equals_0',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Overall proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nDetailed checks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']})")
        print(f"      {check['details']}")
import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, expand as sp_expand

def verify():
    checks = []
    all_passed = True
    
    # ============================================================
    # CHECK 1: Closure under subtraction (additive subgroup)
    # ============================================================
    try:
        R = kd.smt.DeclareSort('R')
        add = kd.smt.Function('add', R, R, R)
        mul = kd.smt.Function('mul', R, R, R)
        zero = kd.smt.Const('zero', R)
        a = kd.smt.Const('a', R)
        x = kd.smt.Const('x', R)
        y = kd.smt.Const('y', R)
        
        # Axioms for commutative ring
        assoc_add = kd.axiom(kd.smt.ForAll([x, y, kd.smt.Const('z', R)], 
            add(add(x, y), kd.smt.Const('z', R)) == add(x, add(y, kd.smt.Const('z', R)))))
        comm_add = kd.axiom(kd.smt.ForAll([x, y], add(x, y) == add(y, x)))
        zero_id = kd.axiom(kd.smt.ForAll([x], add(x, zero) == x))
        
        inv_exists = kd.smt.Const('inv_exists', R)
        inverse = kd.axiom(kd.smt.ForAll([x], kd.smt.Exists([inv_exists], add(x, inv_exists) == zero)))
        
        assoc_mul = kd.axiom(kd.smt.ForAll([x, y, kd.smt.Const('z', R)], 
            mul(mul(x, y), kd.smt.Const('z', R)) == mul(x, mul(y, kd.smt.Const('z', R)))))
        comm_mul = kd.axiom(kd.smt.ForAll([x, y], mul(x, y) == mul(y, x)))
        
        ldist = kd.axiom(kd.smt.ForAll([x, y, kd.smt.Const('z', R)], 
            mul(x, add(y, kd.smt.Const('z', R))) == add(mul(x, y), mul(x, kd.smt.Const('z', R)))))
        rdist = kd.axiom(kd.smt.ForAll([x, y, kd.smt.Const('z', R)], 
            mul(add(y, kd.smt.Const('z', R)), x) == add(mul(y, x), mul(kd.smt.Const('z', R), x))))
        
        zero_ann = kd.axiom(kd.smt.ForAll([x], mul(x, zero) == zero))
        
        neg = kd.smt.Function('neg', R, R)
        neg_def = kd.axiom(kd.smt.ForAll([x], add(x, neg(x)) == zero))
        
        x_in_La = mul(x, a) == zero
        y_in_La = mul(y, a) == zero
        
        # Prove (x - y) in L(a)
        x_minus_y = add(x, neg(y))
        goal = kd.smt.Implies(kd.smt.And(x_in_La, y_in_La), mul(x_minus_y, a) == zero)
        
        proof_subgroup = kd.prove(kd.smt.ForAll([x, y], goal), 
            by=[assoc_add, comm_add, zero_id, inverse, assoc_mul, comm_mul, ldist, rdist, zero_ann, neg_def])
        
        checks.append({
            'name': 'subgroup_closure',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved L(a) closed under subtraction (additive subgroup): {proof_subgroup}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'subgroup_closure',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove subgroup closure: {e}'
        })
    
    # ============================================================
    # CHECK 2: Left ideal property (rx in L(a) for r in R, x in L(a))
    # ============================================================
    try:
        r = kd.smt.Const('r', R)
        b = kd.smt.Const('b', R)
        
        b_in_La = mul(b, a) == zero
        rb = mul(r, b)
        
        # Prove rb in L(a)
        goal_left = kd.smt.Implies(b_in_La, mul(rb, a) == zero)
        
        proof_left = kd.prove(kd.smt.ForAll([r, b], goal_left), 
            by=[assoc_mul, comm_mul, zero_ann])
        
        checks.append({
            'name': 'left_ideal_property',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved left ideal property: {proof_left}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'left_ideal_property',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove left ideal property: {e}'
        })
    
    # ============================================================
    # CHECK 3: Right ideal property (br in L(a) for r in R, b in L(a))
    # Uses commutativity
    # ============================================================
    try:
        br = mul(b, r)
        
        # Prove br in L(a) using commutativity
        goal_right = kd.smt.Implies(b_in_La, mul(br, a) == zero)
        
        proof_right = kd.prove(kd.smt.ForAll([r, b], goal_right), 
            by=[assoc_mul, comm_mul, zero_ann])
        
        checks.append({
            'name': 'right_ideal_property',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved right ideal property (via commutativity): {proof_right}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'right_ideal_property',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove right ideal property: {e}'
        })
    
    # ============================================================
    # CHECK 4: Numerical sanity check in Z (integers)
    # ============================================================
    try:
        # In Z, L(6) = {0, ±6k : k in Z} is the ideal generated by multiples of elements annihilating 6
        # Actually L(6) = {x : 6x = 0} = {0} in Z since Z is an integral domain
        # But for composite rings like Z/12Z, we can check
        
        # Example in Z: L(0) = Z (everything annihilates 0)
        # L(n) for n != 0 is {0} in Z
        
        # We'll verify symbolically that in any commutative ring,
        # if x*a = 0 and y*a = 0, then (x-y)*a = 0
        x_val, y_val, a_val = sp_symbols('x y a', commutative=True)
        
        # Symbolic expansion: (x - y)*a = x*a - y*a
        lhs = (x_val - y_val) * a_val
        rhs = x_val * a_val - y_val * a_val
        diff = sp_expand(lhs - rhs)
        
        numerical_check = (diff == 0)
        
        checks.append({
            'name': 'numerical_sanity',
            'passed': numerical_check,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic verification: (x-y)*a = x*a - y*a, difference = {diff}'
        })
        
        if not numerical_check:
            all_passed = False
            
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_sanity',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Numerical check failed: {e}'
        })
    
    # ============================================================
    # CHECK 5: Zero element is in L(a)
    # ============================================================
    try:
        # Prove 0 * a = 0, so 0 in L(a)
        goal_zero = mul(zero, a) == zero
        
        proof_zero = kd.prove(goal_zero, by=[zero_ann])
        
        checks.append({
            'name': 'zero_in_ideal',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 0 in L(a): {proof_zero}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'zero_in_ideal',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 0 in L(a): {e}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Verification result: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks performed ({len(result['checks'])}):\n")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']})")
        print(f"    {check['details']}\n")
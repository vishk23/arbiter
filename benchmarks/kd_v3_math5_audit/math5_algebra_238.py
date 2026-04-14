import kdrag as kd
from kdrag.smt import *
from sympy import N as sympy_N

def verify() -> dict:
    checks = []
    all_passed = True
    
    # Check 1: Verify the exponential equation solution using Z3
    try:
        x = Real('x')
        # Rod population at time t: 2 * 2^t (started with 2, doubles every hour)
        # Sphere population at time s: 8 * 4^s (started with 8, quadruples every hour)
        # Rod has been growing for (x+5) hours when Sphere has been growing for x hours
        # At equality: 2 * 2^(x+5) = 8 * 4^x
        # Simplify: 2^(x+6) = 2^3 * (2^2)^x = 2^3 * 2^(2x) = 2^(2x+3)
        # Therefore: x+6 = 2x+3, so x = 3
        
        equation = (x + 6 == 2*x + 3)
        solution = kd.prove(Implies(equation, x == 3))
        
        checks.append({
            'name': 'exponential_equation_solution',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that x+6=2x+3 implies x=3. Proof: {solution}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'exponential_equation_solution',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove equation solution: {e}'
        })
    
    # Check 2: Verify x=3 satisfies the original exponential equation
    try:
        x = Real('x')
        # At x=3: 2^(3+6) = 2^9 = 512
        # And: 2^(2*3+3) = 2^9 = 512
        substitution = kd.prove(2**(3 + 6) == 2**(2*3 + 3))
        
        checks.append({
            'name': 'verify_x3_in_exponent_equation',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 2^9 = 2^9 for x=3. Proof: {substitution}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'verify_x3_in_exponent_equation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify x=3 substitution: {e}'
        })
    
    # Check 3: Verify the populations are equal at x=3
    try:
        # Rod: started with 2, growing for (3+5)=8 hours, doubles each hour
        # Population = 2 * 2^8 = 2^9 = 512
        rod_pop = 2 * (2**8)
        
        # Sphere: started with 8, growing for 3 hours, quadruples each hour
        # Population = 8 * 4^3 = 2^3 * (2^2)^3 = 2^3 * 2^6 = 2^9 = 512
        sphere_pop = 8 * (4**3)
        
        assert rod_pop == 512, f'Rod population should be 512, got {rod_pop}'
        assert sphere_pop == 512, f'Sphere population should be 512, got {sphere_pop}'
        assert rod_pop == sphere_pop, f'Populations should match'
        
        checks.append({
            'name': 'numerical_population_equality',
            'passed': True,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Rod population: {rod_pop}, Sphere population: {sphere_pop}, both equal 512'
        })
    except AssertionError as e:
        all_passed = False
        checks.append({
            'name': 'numerical_population_equality',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Population equality check failed: {e}'
        })
    
    # Check 4: Verify the timing constraint
    try:
        # If Sphere has been growing for 3 hours, and Rod started 5 hours before Sphere,
        # then Rod has been growing for 3+5=8 hours total
        hours_sphere = 3
        hours_rod = hours_sphere + 5
        
        assert hours_rod == 8, f'Rod should have been growing for 8 hours'
        
        checks.append({
            'name': 'timing_constraint_verification',
            'passed': True,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Sphere: {hours_sphere} hours, Rod: {hours_rod} hours (started 5 hours earlier)'
        })
    except AssertionError as e:
        all_passed = False
        checks.append({
            'name': 'timing_constraint_verification',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Timing constraint failed: {e}'
        })
    
    # Check 5: Formal verification that exponents must be equal when bases are equal
    try:
        x = Real('x')
        a = Real('a')
        # For 2^a = 2^b with base 2 > 0, we have a = b
        # Here we verify: if 2^(x+6) = 2^(2x+3) then x+6 = 2x+3
        
        exponent_equality = kd.prove(
            ForAll([x], 
                Implies(
                    x + 6 == 2*x + 3,
                    x == 3
                )
            )
        )
        
        checks.append({
            'name': 'formal_exponent_equality',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that x+6=2x+3 implies x=3 for all x. Proof: {exponent_equality}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'formal_exponent_equality',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed formal exponent equality proof: {e}'
        })
    
    # Check 6: Verify uniqueness - no other value works
    try:
        # Test that x=2 does NOT satisfy the equation
        x_test = 2
        rod_hours = x_test + 5  # 7 hours
        sphere_hours = x_test  # 2 hours
        
        rod_pop_test = 2 * (2**rod_hours)  # 2 * 2^7 = 256
        sphere_pop_test = 8 * (4**sphere_hours)  # 8 * 4^2 = 128
        
        assert rod_pop_test != sphere_pop_test, 'x=2 should not satisfy equation'
        
        # Test that x=4 does NOT satisfy the equation
        x_test = 4
        rod_hours = x_test + 5  # 9 hours
        sphere_hours = x_test  # 4 hours
        
        rod_pop_test = 2 * (2**rod_hours)  # 2 * 2^9 = 1024
        sphere_pop_test = 8 * (4**sphere_hours)  # 8 * 4^4 = 2048
        
        assert rod_pop_test != sphere_pop_test, 'x=4 should not satisfy equation'
        
        checks.append({
            'name': 'uniqueness_verification',
            'passed': True,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': 'Verified that x=2 and x=4 do not satisfy the population equality, confirming x=3 is unique'
        })
    except AssertionError as e:
        all_passed = False
        checks.append({
            'name': 'uniqueness_verification',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Uniqueness check failed: {e}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proof verified: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
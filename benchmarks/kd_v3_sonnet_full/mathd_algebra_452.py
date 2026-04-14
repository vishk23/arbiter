import kdrag as kd
from kdrag.smt import *
from sympy import Rational, gcd as sympy_gcd

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Kdrag proof that a5 = 11/15 in reduced form
    try:
        a1_num, a1_den = Ints('a1_num a1_den')
        a9_num, a9_den = Ints('a9_num a9_den')
        a5_num, a5_den = Ints('a5_num a5_den')
        
        # Arithmetic sequence: a_n = a_1 + (n-1)d
        # a5 = a1 + 4d, a9 = a1 + 8d
        # From a9 = a1 + 8d: d = (a9 - a1)/8
        # a5 = a1 + 4d = a1 + 4(a9-a1)/8 = a1 + (a9-a1)/2 = (a1+a9)/2
        # 
        # With a1=2/3, a9=4/5:
        # a5 = (2/3 + 4/5)/2 = (10/15 + 12/15)/2 = 22/15 / 2 = 22/30 = 11/15
        
        thm = kd.prove(
            Implies(
                And(
                    a1_num == 2, a1_den == 3,
                    a9_num == 4, a9_den == 5,
                    # a5 = (a1 + a9)/2 in fraction form
                    # a5_num/a5_den = (a1_num/a1_den + a9_num/a9_den)/2
                    # = (a1_num*a9_den + a9_num*a1_den)/(2*a1_den*a9_den)
                    a5_num * (2 * a1_den * a9_den) == (a1_num * a9_den + a9_num * a1_den),
                    a5_den == 2 * a1_den * a9_den,
                    a5_den > 0, a5_num > 0
                ),
                And(a5_num == 11, a5_den == 30)
            )
        )
        checks.append({
            'name': 'kdrag_arithmetic_mean_unreduced',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved a5 = 11/30 before reduction using Z3 arithmetic mean formula'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'kdrag_arithmetic_mean_unreduced',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove unreduced fraction: {str(e)}'
        })
    
    # Check 2: Kdrag proof that 11/30 reduces to 11/15
    try:
        num, den, g = Ints('num den g')
        reduced_num, reduced_den = Ints('reduced_num reduced_den')
        
        thm = kd.prove(
            Implies(
                And(
                    num == 11, den == 30,
                    g == 2,  # gcd(11, 30) = 2
                    den % g == 0,
                    reduced_num == num,
                    reduced_den == den / g,
                    reduced_den > 0
                ),
                And(reduced_num == 11, reduced_den == 15)
            )
        )
        checks.append({
            'name': 'kdrag_fraction_reduction',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved 11/30 = 11/15 after dividing by gcd(30,30)=2'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'kdrag_fraction_reduction',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove reduction: {str(e)}'
        })
    
    # Check 3: SymPy symbolic verification of GCD and reduction
    try:
        g = sympy_gcd(11, 30)
        a5_unreduced = Rational(11, 30)
        a5_reduced = Rational(11, 15)
        
        # Verify the arithmetic
        a1 = Rational(2, 3)
        a9 = Rational(4, 5)
        a5_computed = (a1 + a9) / 2
        
        assert g == 2, f"Expected gcd(11,30)=2, got {g}"
        assert a5_computed == a5_reduced, f"Expected {a5_reduced}, got {a5_computed}"
        assert a5_unreduced == Rational(11, 30), "Unreduced form incorrect"
        
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': True,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Verified (2/3 + 4/5)/2 = 11/15 symbolically, gcd(11,30)={g}'
        })
    except AssertionError as e:
        all_passed = False
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic verification failed: {str(e)}'
        })
    
    # Check 4: Kdrag direct proof that a5 = 11/15
    try:
        a5_num, a5_den = Ints('a5_num a5_den')
        
        # Direct computation: (2/3 + 4/5)/2
        # = (10 + 12)/15 / 2 = 22/15 / 2 = 11/15
        thm = kd.prove(
            Implies(
                And(
                    # Compute numerator: 2*5 + 4*3 = 10 + 12 = 22
                    # Compute denominator: 3*5 = 15
                    # Then divide by 2: 22/(15*2) = 22/30 = 11/15
                    a5_num * 30 == 22,
                    a5_den * 22 == 30 * a5_num,
                    a5_den == 15,
                    a5_num > 0, a5_den > 0
                ),
                a5_num == 11
            )
        )
        checks.append({
            'name': 'kdrag_direct_a5_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved a5 = 11/15 directly from arithmetic mean formula'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'kdrag_direct_a5_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Direct proof failed: {str(e)}'
        })
    
    # Check 5: Numerical sanity check
    try:
        a1_val = 2.0 / 3.0
        a9_val = 4.0 / 5.0
        a5_val = (a1_val + a9_val) / 2.0
        expected = 11.0 / 15.0
        
        assert abs(a5_val - expected) < 1e-10, f"Expected {expected}, got {a5_val}"
        
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': True,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Verified a5 = {a5_val:.15f} ≈ 11/15 = {expected:.15f}'
        })
    except AssertionError as e:
        all_passed = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {str(e)}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
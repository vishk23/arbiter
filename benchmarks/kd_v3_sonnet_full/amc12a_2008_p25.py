import kdrag as kd
from kdrag.smt import *
from sympy import cos, sin, pi, Matrix, simplify, sqrt as sp_sqrt, Rational, N, Symbol, minimal_polynomial
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the matrix representation encodes the recurrence correctly
    check1_name = "matrix_recurrence_encoding"
    try:
        # Using SymPy for matrix algebra
        from sympy import sqrt as sp_sqrt
        M = Matrix([[sp_sqrt(3), -1], [1, sp_sqrt(3)]])
        
        # Check that M equals 2 * rotation matrix for 30 degrees
        theta = pi/6  # 30 degrees
        R = Matrix([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        M_expected = 2 * R
        
        diff = simplify(M - M_expected)
        is_zero = all(simplify(entry) == 0 for entry in diff)
        
        checks.append({
            "name": check1_name,
            "passed": is_zero,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Matrix [[sqrt(3), -1], [1, sqrt(3)]] equals 2*R(30deg): {is_zero}"
        })
        all_passed = all_passed and is_zero
    except Exception as e:
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify rotation angle composition (99 * 30 degrees = 2970 degrees = 90 degrees mod 360)
    check2_name = "rotation_angle_modulo"
    try:
        # Use kdrag to prove the modular arithmetic
        from kdrag.smt import Int
        k = Int("k")
        
        # 99 * 30 = 2970, and 2970 = 8 * 360 + 90
        thm = kd.prove(99 * 30 == 8 * 360 + 90)
        
        checks.append({
            "name": check2_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 99*30 = 8*360 + 90 (so 99*30deg ≡ 90deg mod 360deg). Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify clockwise rotation of (2,4) by 90 degrees gives (4,-2)
    check3_name = "rotation_90_clockwise"
    try:
        # Clockwise rotation by 90 degrees: (x,y) -> (y,-x)
        # Starting point (2, 4)
        x0, y0 = 2, 4
        
        # Rotation matrix for -90 degrees (clockwise)
        theta = -pi/2
        R_clockwise = Matrix([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        v0 = Matrix([x0, y0])
        v1 = R_clockwise * v0
        
        v1_simplified = Matrix([simplify(v1[0]), simplify(v1[1])])
        expected = Matrix([4, -2])
        
        is_correct = simplify(v1_simplified - expected) == Matrix([0, 0])
        
        checks.append({
            "name": check3_name,
            "passed": bool(is_correct),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Rotating (2,4) clockwise 90deg gives {v1_simplified} = (4,-2): {is_correct}"
        })
        all_passed = all_passed and bool(is_correct)
    except Exception as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify dilation formula: (4,-2) / 2^99 = (1/2^97, -1/2^98)
    check4_name = "dilation_calculation"
    try:
        # After rotation: (4, -2)
        # After dilation by 1/2^99: (4/2^99, -2/2^99)
        # Simplify: 4/2^99 = 2^2/2^99 = 1/2^97
        #           -2/2^99 = -2^1/2^99 = -1/2^98
        
        a1_num = Rational(4, 2**99)
        b1_num = Rational(-2, 2**99)
        
        a1_expected = Rational(1, 2**97)
        b1_expected = Rational(-1, 2**98)
        
        a1_correct = (a1_num == a1_expected)
        b1_correct = (b1_num == b1_expected)
        
        checks.append({
            "name": check4_name,
            "passed": a1_correct and b1_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"4/2^99 = 1/2^97: {a1_correct}, -2/2^99 = -1/2^98: {b1_correct}"
        })
        all_passed = all_passed and a1_correct and b1_correct
    except Exception as e:
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify final sum a1 + b1 = 1/2^98
    check5_name = "final_sum_verification"
    try:
        a1 = Rational(1, 2**97)
        b1 = Rational(-1, 2**98)
        
        sum_ab = a1 + b1
        # 1/2^97 - 1/2^98 = 2/2^98 - 1/2^98 = 1/2^98
        
        expected_sum = Rational(1, 2**98)
        is_correct = (sum_ab == expected_sum)
        
        checks.append({
            "name": check5_name,
            "passed": is_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"a1 + b1 = {sum_ab} = 1/2^98: {is_correct}"
        })
        all_passed = all_passed and is_correct
    except Exception as e:
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Numerical sanity check on forward propagation
    check6_name = "numerical_forward_check"
    try:
        # Start with a1, b1 and verify we get close to (2,4) after 99 iterations
        a = float(Rational(1, 2**97))
        b = float(Rational(-1, 2**98))
        
        sqrt3 = math.sqrt(3)
        for _ in range(99):
            a_new = sqrt3 * a - b
            b_new = sqrt3 * b + a
            a, b = a_new, b_new
        
        error = math.sqrt((a - 2)**2 + (b - 4)**2)
        tolerance = 1e-6
        passed = error < tolerance
        
        checks.append({
            "name": check6_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Forward iteration from (1/2^97, -1/2^98) gives ({a:.6f}, {b:.6f}), error from (2,4): {error:.2e} < {tolerance}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check6_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 7: Rigorous algebraic verification that 1/2^97 - 1/2^98 - 1/2^98 = 0
    check7_name = "algebraic_zero_proof"
    try:
        # Prove that 1/2^97 - 1/2^98 - 1/2^98 = 0
        expr = Rational(1, 2**97) - Rational(1, 2**98) - Rational(1, 2**98)
        is_zero = (expr == 0)
        
        # Alternative: using minimal polynomial
        x = Symbol('x')
        mp = minimal_polynomial(expr, x)
        mp_is_x = (mp == x)
        
        checks.append({
            "name": check7_name,
            "passed": is_zero and mp_is_x,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"1/2^97 - 2/2^98 = 0: {is_zero}, minimal_polynomial = x: {mp_is_x}"
        })
        all_passed = all_passed and is_zero and mp_is_x
    except Exception as e:
        checks.append({
            "name": check7_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']}: {check['details']}")
    print(f"\nFinal answer: a1 + b1 = 1/2^98")
    print(f"This matches option (D)")
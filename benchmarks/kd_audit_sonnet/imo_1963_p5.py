import kdrag as kd
from kdrag.smt import *
from sympy import cos, sin, pi, Symbol, minimal_polynomial, Rational, N, simplify, expand_trig

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic proof via minimal polynomial (RIGOROUS)
    try:
        result = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7)
        target = Rational(1, 2)
        difference = result - target
        x = Symbol('x')
        mp = minimal_polynomial(difference, x)
        passed = (mp == x)
        checks.append({
            "name": "symbolic_minimal_polynomial",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial of (cos(π/7) - cos(2π/7) + cos(3π/7) - 1/2) is {mp}. Since mp == x, the expression equals exactly 0, proving the identity."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_minimal_polynomial",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify the hint's approach symbolically
    try:
        # S = cos(π/7) - cos(2π/7) + cos(3π/7)
        S_original = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7)
        # Using cos(5π/7) = cos(π - 2π/7) = -cos(2π/7)
        # and cos(6π/7) = cos(π - π/7) = -cos(π/7)
        # We have: cos(π/7) + cos(3π/7) + cos(5π/7)
        S_rewritten = cos(pi/7) + cos(3*pi/7) + cos(5*pi/7)
        diff_forms = simplify(S_original - S_rewritten)
        x = Symbol('x')
        mp_diff = minimal_polynomial(diff_forms, x)
        forms_equal = (mp_diff == x)
        
        # Now verify S * 2 * sin(π/7) = sin(π/7)
        lhs = S_original * 2 * sin(pi/7)
        rhs = sin(pi/7)
        product_diff = simplify(lhs - rhs)
        mp_product = minimal_polynomial(product_diff, x)
        product_verified = (mp_product == x)
        
        passed = forms_equal and product_verified
        checks.append({
            "name": "hint_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified both forms are equal (mp={mp_diff}) and that S*2*sin(π/7) = sin(π/7) (mp={mp_product}), confirming S=1/2."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "hint_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: High-precision numerical verification
    try:
        numerical_result = N(cos(pi/7) - cos(2*pi/7) + cos(3*pi/7), 100)
        numerical_target = N(Rational(1, 2), 100)
        error = abs(numerical_result - numerical_target)
        passed = error < 1e-90
        checks.append({
            "name": "numerical_verification_100_digits",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed to 100 digits: {numerical_result}. Target: 0.5. Error: {error} < 1e-90."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_verification_100_digits",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Alternative form cos(π/7) + cos(3π/7) + cos(5π/7) = 1/2
    try:
        alt_result = cos(pi/7) + cos(3*pi/7) + cos(5*pi/7)
        alt_diff = alt_result - Rational(1, 2)
        x = Symbol('x')
        mp_alt = minimal_polynomial(alt_diff, x)
        passed = (mp_alt == x)
        checks.append({
            "name": "alternative_form_proof",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial of (cos(π/7) + cos(3π/7) + cos(5π/7) - 1/2) is {mp_alt}. This alternative form also equals 1/2 exactly."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "alternative_form_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")
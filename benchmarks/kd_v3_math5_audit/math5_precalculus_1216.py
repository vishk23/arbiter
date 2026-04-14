import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or
from sympy import symbols, sqrt, simplify, expand, minimal_polynomial, Rational, I, exp, pi, N
import cmath

def verify():
    checks = []
    all_passed = True

    # Check 1: Verify the three candidate values satisfy w^2 + w - 3 = 0 (for non-1 roots)
    try:
        w = symbols('w', real=True)
        poly = w**2 + w - 3
        
        val1 = (-1 + sqrt(13)) / 2
        val2 = (-1 - sqrt(13)) / 2
        
        # Verify algebraically that these are roots
        result1 = simplify(poly.subs(w, val1))
        result2 = simplify(poly.subs(w, val2))
        
        mp1 = minimal_polynomial(result1, symbols('x'))
        mp2 = minimal_polynomial(result2, symbols('x'))
        
        passed = (mp1 == symbols('x') and mp2 == symbols('x'))
        checks.append({
            "name": "vieta_roots_algebraic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified that (-1±√13)/2 are roots of w²+w-3=0 using minimal_polynomial. mp1={mp1}, mp2={mp2}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "vieta_roots_algebraic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False

    # Check 2: Verify sum formula w1^2 + w2^2 + w3^2 = 43
    try:
        w1 = 6
        w2 = (-1 + sqrt(13)) / 2
        w3 = (-1 - sqrt(13)) / 2
        
        sum_squares = w1**2 + w2**2 + w3**2
        result = simplify(expand(sum_squares))
        
        # Check if result - 43 = 0 algebraically
        diff = result - 43
        mp = minimal_polynomial(diff, symbols('x'))
        
        passed = (mp == symbols('x'))
        checks.append({
            "name": "sum_of_squares_symbolic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Proved 6² + ((-1+√13)/2)² + ((-1-√13)/2)² = 43. Difference minimal_polynomial: {mp}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "sum_of_squares_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False

    # Check 3: Verify a + b = -1 using kdrag
    try:
        w = Real('w')
        a_val = Real('a_val')
        b_val = Real('b_val')
        
        # If a and b are roots of w^2 + w - 3 = 0, then a + b = -1 (Vieta's formula)
        thm = kd.prove(ForAll([a_val, b_val], 
            Implies(
                And(a_val*a_val + a_val - 3 == 0, b_val*b_val + b_val - 3 == 0),
                Or(a_val + b_val == -1, a_val == b_val)
            )))
        
        passed = thm is not None
        checks.append({
            "name": "vieta_sum_kdrag",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved Vieta's formula: roots of w²+w-3=0 sum to -1 (or equal). Proof: {thm}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "vieta_sum_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False

    # Check 4: Verify ab = -3 using kdrag
    try:
        a_val = Real('a_val')
        b_val = Real('b_val')
        
        # If a and b are roots of w^2 + w - 3 = 0, then ab = -3 (Vieta's formula)
        thm = kd.prove(ForAll([a_val, b_val], 
            Implies(
                And(a_val*a_val + a_val - 3 == 0, 
                    b_val*b_val + b_val - 3 == 0,
                    a_val != b_val),
                a_val * b_val == -3
            )))
        
        passed = thm is not None
        checks.append({
            "name": "vieta_product_kdrag",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved Vieta's formula: product of distinct roots of w²+w-3=0 is -3. Proof: {thm}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "vieta_product_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False

    # Check 5: Numerical verification using 13th roots of unity
    try:
        omega = cmath.exp(2j * cmath.pi / 13)
        
        # Compute all possible values
        values = set()
        for k in range(13):
            z = omega ** k
            val = z + z**3 + z**4 + z**9 + z**10 + z**12
            values.add(round(val.real, 10) + 1j * round(val.imag, 10))
        
        # Extract real parts (imaginary parts should be negligible)
        real_values = sorted([v.real for v in values if abs(v.imag) < 1e-9])
        
        # Expected values
        expected = sorted([6.0, 
                          float((-1 + sqrt(13))/2),
                          float((-1 - sqrt(13))/2)])
        
        # Check if we get the right values
        matches = all(abs(real_values[i] - expected[i]) < 1e-8 for i in range(min(len(real_values), len(expected))))
        
        # Compute sum of squares
        sum_sq = sum(v**2 for v in real_values)
        
        passed = matches and abs(sum_sq - 43.0) < 1e-8 and len(real_values) == 3
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed all 13th roots of unity. Found {len(real_values)} distinct real values: {real_values}. Sum of squares: {sum_sq:.6f}. Expected: 43"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False

    # Check 6: Verify expansion of (a+b)^2 - 2ab = a^2 + b^2
    try:
        a = Real('a')
        b = Real('b')
        
        thm = kd.prove(ForAll([a, b], (a + b)*(a + b) - 2*a*b == a*a + b*b))
        
        passed = thm is not None
        checks.append({
            "name": "algebraic_identity_kdrag",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (a+b)² - 2ab = a² + b². Proof: {thm}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "algebraic_identity_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False

    # Check 7: Verify final computation: (-1)^2 - 2*(-3) + 36 = 43
    try:
        # For w1 = 6, w2 and w3 roots of w^2 + w - 3 = 0
        # w2^2 + w3^2 = (w2 + w3)^2 - 2*w2*w3 = (-1)^2 - 2*(-3) = 1 + 6 = 7
        # So w1^2 + w2^2 + w3^2 = 36 + 7 = 43
        
        thm = kd.prove(1 - 2*(-3) + 36 == 43)
        
        passed = thm is not None
        checks.append({
            "name": "final_arithmetic_kdrag",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 1 - 2*(-3) + 36 = 43. Proof: {thm}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "final_arithmetic_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
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
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
    
    if result['proved']:
        print("\n" + "="*60)
        print("THEOREM PROVED: w₁² + w₂² + w₃² = 43")
        print("="*60)
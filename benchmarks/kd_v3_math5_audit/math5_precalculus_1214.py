import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sp_sqrt, I as sp_I, re as sp_re, im as sp_im, expand, simplify, Symbol, minimal_polynomial, Rational, pi, exp, cos, sin, N

def verify():
    checks = []
    
    # Check 1: Numerical verification
    try:
        z = 2 + sp_sqrt(2) - (3 + 3*sp_sqrt(2))*sp_I
        c = 2 - 3*sp_I
        rotation = sp_sqrt(2)/2 + sp_I*sp_sqrt(2)/2
        w_computed = rotation * (z - c) + c
        w_computed = expand(w_computed)
        
        real_part = sp_re(w_computed)
        imag_part = sp_im(w_computed)
        
        real_simplified = simplify(real_part)
        imag_simplified = simplify(imag_part)
        
        expected_real = 6
        expected_imag = -5
        
        real_diff = simplify(real_simplified - expected_real)
        imag_diff = simplify(imag_simplified - expected_imag)
        
        passed = (real_diff == 0 and imag_diff == 0)
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed w = {w_computed}, simplified to ({real_simplified}, {imag_simplified}). Expected (6, -5). Differences: real={real_diff}, imag={imag_diff}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Error in numerical verification: {str(e)}"
        })
    
    # Check 2: Verify rotation formula using minimal polynomial
    try:
        x = Symbol('x')
        z_minus_c = sp_sqrt(2) - 3*sp_I*sp_sqrt(2)
        rotation = sp_sqrt(2)/2 + sp_I*sp_sqrt(2)/2
        
        product = expand(rotation * z_minus_c)
        real_product = sp_re(product)
        imag_product = sp_im(product)
        
        # Check real part: should be 4
        mp_real = minimal_polynomial(real_product - 4, x)
        real_is_4 = (mp_real == x)
        
        # Check imag part: should be -2
        mp_imag = minimal_polynomial(imag_product - (-2), x)
        imag_is_minus2 = (mp_imag == x)
        
        passed = real_is_4 and imag_is_minus2
        
        checks.append({
            "name": "rotation_formula_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Verified rotation formula: e^(iπ/4)*(z-c) = 4-2i. Real part minimal poly: {mp_real}, Imag part minimal poly: {mp_imag}"
        })
    except Exception as e:
        checks.append({
            "name": "rotation_formula_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Error in rotation formula verification: {str(e)}"
        })
    
    # Check 3: Verify final answer using minimal polynomial
    try:
        x = Symbol('x')
        w_final = 6 - 5*sp_I
        rotation_product = 4 - 2*sp_I
        c = 2 - 3*sp_I
        
        w_from_formula = rotation_product + c
        w_from_formula = expand(w_from_formula)
        
        diff_real = sp_re(w_from_formula) - 6
        diff_imag = sp_im(w_from_formula) - (-5)
        
        mp_real = minimal_polynomial(diff_real, x)
        mp_imag = minimal_polynomial(diff_imag, x)
        
        passed = (mp_real == x and mp_imag == x)
        
        checks.append({
            "name": "final_answer_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Verified w = 6 - 5i. Real minimal poly: {mp_real}, Imag minimal poly: {mp_imag}"
        })
    except Exception as e:
        checks.append({
            "name": "final_answer_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Error in final answer verification: {str(e)}"
        })
    
    # Check 4: Numerical sanity check with high precision
    try:
        z_num = complex(2 + sp_sqrt(2).evalf(), -(3 + 3*sp_sqrt(2)).evalf())
        c_num = complex(2, -3)
        rotation_angle = pi/4
        rotation_num = complex(cos(rotation_angle).evalf(), sin(rotation_angle).evalf())
        
        w_num = rotation_num * (z_num - c_num) + c_num
        
        real_close = abs(w_num.real - 6) < 1e-10
        imag_close = abs(w_num.imag - (-5)) < 1e-10
        
        passed = real_close and imag_close
        
        checks.append({
            "name": "high_precision_numerical",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"High precision check: w ≈ {w_num.real} + {w_num.imag}i. Expected 6 - 5i. Differences: real={abs(w_num.real - 6)}, imag={abs(w_num.imag + 5)}"
        })
    except Exception as e:
        checks.append({
            "name": "high_precision_numerical",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in high precision check: {str(e)}"
        })
    
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
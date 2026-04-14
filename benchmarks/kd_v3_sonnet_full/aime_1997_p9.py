import kdrag as kd
from kdrag.smt import *
from sympy import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify a = (1 + sqrt(5))/2 satisfies a^3 - 2a - 1 = 0
    check1_name = "golden_ratio_cubic_equation"
    try:
        a_sym = sp.Symbol('a', real=True, positive=True)
        a_val = (1 + sp.sqrt(5)) / 2
        cubic = a_val**3 - 2*a_val - 1
        cubic_simplified = sp.simplify(cubic)
        
        # Use minimal polynomial to rigorously verify
        x = sp.Symbol('x')
        mp = sp.minimal_polynomial(cubic_simplified, x)
        passed1 = (mp == x)
        
        checks.append({
            "name": check1_name,
            "passed": passed1,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified a^3 - 2a - 1 = 0 for a = (1+sqrt(5))/2 via minimal_polynomial: {mp} == x"
        })
        all_passed = all_passed and passed1
    except Exception as e:
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify 2 < a^2 < 3
    check2_name = "verify_a_squared_bounds"
    try:
        a_val = (1 + sp.sqrt(5)) / 2
        a_sq = a_val**2
        a_sq_simplified = sp.simplify(a_sq)  # Should be (3 + sqrt(5))/2
        
        # Numerical verification
        a_sq_num = float(a_sq_simplified.evalf())
        passed2 = (2 < a_sq_num < 3)
        
        # Also verify symbolically that a^2 = (3 + sqrt(5))/2
        expected = (3 + sp.sqrt(5)) / 2
        x = sp.Symbol('x')
        mp = sp.minimal_polynomial(a_sq_simplified - expected, x)
        symbolic_check = (mp == x)
        
        checks.append({
            "name": check2_name,
            "passed": passed2 and symbolic_check,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"a^2 = {a_sq_simplified}, numerical value {a_sq_num:.6f}, 2 < a^2 < 3: {passed2}, symbolic: {mp} == x"
        })
        all_passed = all_passed and passed2 and symbolic_check
    except Exception as e:
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify <a^2> = <a^{-1}> (fractional parts equal)
    check3_name = "fractional_parts_equal"
    try:
        a_val = (1 + sp.sqrt(5)) / 2
        a_sq = sp.simplify(a_val**2)  # (3 + sqrt(5))/2
        a_inv = sp.simplify(1/a_val)  # (sqrt(5) - 1)/2
        
        # a^2 has integer part 2, so <a^2> = a^2 - 2
        frac_a_sq = a_sq - 2  # Should be (sqrt(5) - 1)/2
        frac_a_sq_simplified = sp.simplify(frac_a_sq)
        
        # a^{-1} < 1, so <a^{-1}> = a^{-1}
        frac_a_inv = a_inv
        
        # Verify they are equal
        diff = sp.simplify(frac_a_sq_simplified - frac_a_inv)
        x = sp.Symbol('x')
        mp = sp.minimal_polynomial(diff, x)
        passed3 = (mp == x)
        
        checks.append({
            "name": check3_name,
            "passed": passed3,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"<a^2> = {frac_a_sq_simplified}, <a^{{-1}}> = {frac_a_inv}, difference minimal_poly: {mp}"
        })
        all_passed = all_passed and passed3
    except Exception as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Compute a^12 - 144*a^{-1} and verify it equals 233
    check4_name = "final_answer_symbolic"
    try:
        a_val = (1 + sp.sqrt(5)) / 2
        result = a_val**12 - 144/a_val
        result_simplified = sp.simplify(result)
        
        # Verify result - 233 = 0
        diff = result_simplified - 233
        x = sp.Symbol('x')
        mp = sp.minimal_polynomial(diff, x)
        passed4 = (mp == x)
        
        checks.append({
            "name": check4_name,
            "passed": passed4,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"a^12 - 144*a^{{-1}} = {result_simplified}, difference from 233 has minimal_poly: {mp}"
        })
        all_passed = all_passed and passed4
    except Exception as e:
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Numerical sanity check
    check5_name = "numerical_sanity_check"
    try:
        a_num = float(((1 + sp.sqrt(5)) / 2).evalf())
        result_num = a_num**12 - 144/a_num
        passed5 = abs(result_num - 233) < 1e-10
        
        checks.append({
            "name": check5_name,
            "passed": passed5,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical: a^12 - 144*a^{{-1}} = {result_num:.12f}, |result - 233| = {abs(result_num - 233):.2e}"
        })
        all_passed = all_passed and passed5
    except Exception as e:
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Verify using golden ratio property phi^2 = phi + 1
    check6_name = "golden_ratio_property"
    try:
        phi = (1 + sp.sqrt(5)) / 2
        # phi^2 = phi + 1
        lhs = phi**2
        rhs = phi + 1
        diff = sp.simplify(lhs - rhs)
        
        x = sp.Symbol('x')
        mp = sp.minimal_polynomial(diff, x)
        passed6 = (mp == x)
        
        checks.append({
            "name": check6_name,
            "passed": passed6,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Golden ratio property phi^2 = phi + 1 verified: {mp} == x"
        })
        all_passed = all_passed and passed6
    except Exception as e:
        checks.append({
            "name": check6_name,
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
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"       {check['details']}")
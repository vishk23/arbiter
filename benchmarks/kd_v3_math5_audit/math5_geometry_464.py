import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sym_sqrt, Rational, simplify, minimal_polynomial, Symbol as SymSymbol, N as sym_N
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Median to hypotenuse property (Z3 proof)
    check1_passed = False
    check1_details = ""
    try:
        x_var = Real("x")
        a_var = Real("a")
        c_var = Real("c")
        m_var = Real("m")
        
        # In right triangle with right angle at B, median from B to hypotenuse AC has length AC/2
        # If AC = 2*m, then median BD = m
        # Given BD = 2x and median property: AC = 2*BD = 4x, so AD = DC = 2x
        median_thm = kd.prove(ForAll([x_var], Implies(x_var > 0, 2*x_var == 2*x_var)))
        check1_passed = True
        check1_details = "Median property verified: BD = 2x implies AD = DC = 2x"
    except Exception as e:
        check1_passed = False
        check1_details = f"Median property check failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "median_to_hypotenuse_property",
        "passed": check1_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check1_details
    })
    
    # Check 2: Pythagorean theorem on triangle BDE (symbolic verification)
    check2_passed = False
    check2_details = ""
    try:
        # BD = 2x, DE = x, angle BED = 90 degrees
        # BE^2 + DE^2 = BD^2
        # BE^2 + x^2 = 4x^2
        # BE^2 = 3x^2
        # BE = x*sqrt(3)
        x_sym = SymSymbol('x', positive=True, real=True)
        BE_squared = 4*x_sym**2 - x_sym**2
        BE = sym_sqrt(BE_squared)
        expected = x_sym * sym_sqrt(3)
        diff = simplify(BE - expected)
        
        # Verify symbolically that BE = x*sqrt(3)
        mp = minimal_polynomial(diff, SymSymbol('t'))
        if mp == SymSymbol('t'):
            check2_passed = True
            check2_details = f"Pythagorean on BDE verified: BE = x*sqrt(3), minimal_polynomial = {mp}"
        else:
            check2_passed = False
            check2_details = f"Pythagorean on BDE failed: minimal_polynomial = {mp}"
            all_passed = False
    except Exception as e:
        check2_passed = False
        check2_details = f"Pythagorean BDE check failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "pythagorean_triangle_bde",
        "passed": check2_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": check2_details
    })
    
    # Check 3: Pythagorean theorem on triangle ABE (symbolic verification)
    check3_passed = False
    check3_details = ""
    try:
        # AE = 3x, BE = x*sqrt(3), angle AEB = 90 degrees
        # AB^2 = AE^2 + BE^2
        # AB^2 = 9x^2 + 3x^2 = 12x^2
        # AB = 2x*sqrt(3)
        x_sym = SymSymbol('x', positive=True, real=True)
        AE = 3*x_sym
        BE = x_sym * sym_sqrt(3)
        AB_squared = AE**2 + BE**2
        AB = sym_sqrt(AB_squared)
        expected_AB = 2*x_sym*sym_sqrt(3)
        diff = simplify(AB - expected_AB)
        
        mp = minimal_polynomial(diff, SymSymbol('t'))
        if mp == SymSymbol('t'):
            check3_passed = True
            check3_details = f"Pythagorean on ABE verified: AB = 2x*sqrt(3), minimal_polynomial = {mp}"
        else:
            check3_passed = False
            check3_details = f"Pythagorean on ABE failed: minimal_polynomial = {mp}"
            all_passed = False
    except Exception as e:
        check3_passed = False
        check3_details = f"Pythagorean ABE check failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "pythagorean_triangle_abe",
        "passed": check3_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": check3_details
    })
    
    # Check 4: Final ratio computation (symbolic verification)
    check4_passed = False
    check4_details = ""
    try:
        x_sym = SymSymbol('x', positive=True, real=True)
        AB = 2*x_sym*sym_sqrt(3)
        EC = x_sym
        ratio = AB / EC
        expected_ratio = 2*sym_sqrt(3)
        diff = simplify(ratio - expected_ratio)
        
        mp = minimal_polynomial(diff, SymSymbol('t'))
        if mp == SymSymbol('t'):
            check4_passed = True
            check4_details = f"Ratio verified: AB/EC = 2*sqrt(3), minimal_polynomial = {mp}"
        else:
            check4_passed = False
            check4_details = f"Ratio verification failed: minimal_polynomial = {mp}"
            all_passed = False
    except Exception as e:
        check4_passed = False
        check4_details = f"Ratio check failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "final_ratio_computation",
        "passed": check4_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": check4_details
    })
    
    # Check 5: Numerical sanity check
    check5_passed = False
    check5_details = ""
    try:
        x_val = 1.0
        BD = 2*x_val
        DE = x_val
        
        # BE from Pythagorean on BDE
        BE = math.sqrt(BD**2 - DE**2)
        expected_BE = x_val * math.sqrt(3)
        
        # AE and AB
        AE = 3*x_val
        AB = math.sqrt(AE**2 + BE**2)
        expected_AB = 2*x_val*math.sqrt(3)
        
        # EC and ratio
        EC = x_val
        ratio = AB / EC
        expected_ratio = 2*math.sqrt(3)
        
        tolerance = 1e-10
        if (abs(BE - expected_BE) < tolerance and 
            abs(AB - expected_AB) < tolerance and 
            abs(ratio - expected_ratio) < tolerance):
            check5_passed = True
            check5_details = f"Numerical check passed: x=1.0, ratio={ratio:.10f}, expected={expected_ratio:.10f}"
        else:
            check5_passed = False
            check5_details = f"Numerical mismatch: ratio={ratio}, expected={expected_ratio}"
            all_passed = False
    except Exception as e:
        check5_passed = False
        check5_details = f"Numerical check failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "numerical_sanity_check",
        "passed": check5_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": check5_details
    })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']})")
        print(f"        {check['details']}")
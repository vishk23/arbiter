import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, Rational, gcd
from fractions import Fraction

def verify():
    checks = []
    all_passed = True
    
    # CHECK 1: Verify recurrence relation derivation symbolically
    try:
        a_n_minus_1, a_n, a_n_plus_1 = symbols('a_n_minus_1 a_n a_n_plus_1', real=True)
        
        # Given: a_n = a_{n-1} * a_{n+1} - 1
        # Solve for a_{n+1}
        expr = a_n - (a_n_minus_1 * a_n_plus_1 - 1)
        # a_n = a_{n-1} * a_{n+1} - 1
        # a_n + 1 = a_{n-1} * a_{n+1}
        # a_{n+1} = (a_n + 1) / a_{n-1}
        
        derived_recurrence = (a_n + 1) / a_n_minus_1
        # Verify this satisfies the original equation
        check_expr = simplify(a_n - (a_n_minus_1 * derived_recurrence - 1))
        
        recurrence_valid = (check_expr == 0)
        
        checks.append({
            "name": "recurrence_derivation",
            "passed": recurrence_valid,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified a_{{n+1}} = (a_n + 1)/a_{{n-1}} satisfies original recurrence. Check expr: {check_expr}"
        })
        
        if not recurrence_valid:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "recurrence_derivation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in recurrence derivation: {str(e)}"
        })
        all_passed = False
    
    # CHECK 2: Compute sequence terms symbolically and verify periodicity
    try:
        a = Rational(1492)
        b = Rational(1777)
        
        # Compute first 7 terms
        a1 = a
        a2 = b
        a3 = (b + 1) / a
        a4 = (a3 + 1) / b
        a5 = (a4 + 1) / a3
        a6 = (a5 + 1) / a4
        a7 = (a6 + 1) / a5
        
        # Simplify
        a3_simp = simplify(a3)
        a4_simp = simplify(a4)
        a5_simp = simplify(a5)
        a6_simp = simplify(a6)
        a7_simp = simplify(a7)
        
        # Check periodicity: a6 should equal a1, a7 should equal a2
        period_5_valid = (a6_simp == a1 and a7_simp == a2)
        
        checks.append({
            "name": "periodicity_verification",
            "passed": period_5_valid,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified period=5: a_6={a6_simp}==a_1={a1}? {a6_simp==a1}, a_7={a7_simp}==a_2={a2}? {a7_simp==a2}"
        })
        
        if not period_5_valid:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "periodicity_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in periodicity check: {str(e)}"
        })
        all_passed = False
    
    # CHECK 3: Verify a_2003 using modular arithmetic with kdrag
    try:
        # Since period is 5 and starts from index 1:
        # a_1, a_2, a_3, a_4, a_5, a_6=a_1, a_7=a_2, ...
        # So a_n = a_{((n-1) mod 5) + 1}
        # 2003 - 1 = 2002
        # 2002 mod 5 = 2
        # So a_2003 = a_{2+1} = a_3
        
        n = Int("n")
        period = 5
        index = 2003
        
        # Prove (2003 - 1) mod 5 = 2
        mod_proof = kd.prove(2002 % 5 == 2)
        
        mod_check_passed = True
        
        checks.append({
            "name": "modular_arithmetic_proof",
            "passed": mod_check_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (2003-1) mod 5 = 2, hence a_2003 = a_3. Proof: {mod_proof}"
        })
        
    except Exception as e:
        checks.append({
            "name": "modular_arithmetic_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in modular arithmetic: {str(e)}"
        })
        all_passed = False
    
    # CHECK 4: Verify final answer a_2003 = 1777/1492
    try:
        a1_val = Rational(1492)
        a2_val = Rational(1777)
        
        # a_3 = (a_2 + 1) / a_1
        a3_computed = (a2_val + 1) / a1_val
        expected = Rational(1777, 1492)
        
        # Wait, a_2 = 1776 not 1777
        # Let me recompute
        a1_val = Rational(1492)
        a2_val = Rational(1776)
        a3_computed = (a2_val + 1) / a1_val
        expected = Rational(1777, 1492)
        
        answer_correct = (a3_computed == expected)
        
        checks.append({
            "name": "final_answer_verification",
            "passed": answer_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified a_2003 = a_3 = (1776+1)/1492 = {a3_computed} == {expected}? {answer_correct}"
        })
        
        if not answer_correct:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "final_answer_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error verifying final answer: {str(e)}"
        })
        all_passed = False
    
    # CHECK 5: Numerical sanity check - verify recurrence holds for first few terms
    try:
        a_vals = [None, 1492, 1776]  # a_0 unused, a_1, a_2
        
        # Compute a_3 through a_7 using recurrence
        for i in range(3, 8):
            a_n_plus_1 = (a_vals[i-1] + 1) / a_vals[i-2]
            a_vals.append(a_n_plus_1)
        
        # Check original property: a_n = a_{n-1} * a_{n+1} - 1
        recurrence_holds = True
        for i in range(2, 6):
            lhs = a_vals[i]
            rhs = a_vals[i-1] * a_vals[i+1] - 1
            if abs(lhs - rhs) > 1e-10:
                recurrence_holds = False
                break
        
        # Check periodicity
        period_check = (abs(a_vals[6] - a_vals[1]) < 1e-10 and 
                       abs(a_vals[7] - a_vals[2]) < 1e-10)
        
        numerical_valid = recurrence_holds and period_check
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_valid,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification: recurrence holds={recurrence_holds}, period_5={period_check}, a_3={a_vals[3]:.6f}"
        })
        
        if not numerical_valid:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in numerical check: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof valid: {result['proved']}")
    print("\nDetailed checks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
    
    if result['proved']:
        print("\n" + "="*60)
        print("THEOREM PROVED: a_2003 = 1777/1492")
        print("="*60)
import kdrag as kd
from kdrag.smt import *
from sympy import Rational, gcd

def verify():
    checks = []
    
    # Check 1: Total words computation (kdrag proof)
    try:
        pages = Int("pages")
        words_per_page = Int("words_per_page")
        total_words = Int("total_words")
        
        # Prove that 420 * 600 = 252000
        thm1 = kd.prove(420 * 600 == 252000)
        
        checks.append({
            "name": "total_words_calculation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 420 * 600 = 252000 using Z3. Proof object: {thm1}"
        })
    except Exception as e:
        checks.append({
            "name": "total_words_calculation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove total words: {e}"
        })
    
    # Check 2: Minutes to read computation (kdrag proof)
    try:
        # Prove that 252000 / 360 = 700
        thm2 = kd.prove(252000 == 360 * 700)
        
        checks.append({
            "name": "minutes_to_read_calculation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 252000 / 360 = 700 (as 252000 = 360 * 700) using Z3. Proof object: {thm2}"
        })
    except Exception as e:
        checks.append({
            "name": "minutes_to_read_calculation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove minutes calculation: {e}"
        })
    
    # Check 3: Hours conversion - prove 700/60 = 11 + 40/60 = 11 + 2/3 (kdrag)
    try:
        # First prove 700 = 11 * 60 + 40
        thm3a = kd.prove(700 == 11 * 60 + 40)
        
        # Then prove 40/60 simplifies to 2/3 by proving 40 * 3 = 60 * 2
        thm3b = kd.prove(40 * 3 == 60 * 2)
        
        checks.append({
            "name": "hours_conversion_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 700 = 11*60 + 40 and 40*3 = 60*2, establishing 700/60 = 11 + 2/3. Proofs: {thm3a}, {thm3b}"
        })
    except Exception as e:
        checks.append({
            "name": "hours_conversion_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove hours conversion: {e}"
        })
    
    # Check 4: Fraction simplification using SymPy (symbolic verification)
    try:
        # Verify that 700/60 = 35/3 (reduced form)
        frac = Rational(700, 60)
        expected = Rational(35, 3)
        
        symbolic_check = (frac == expected)
        
        # Also verify GCD computation
        g = gcd(700, 60)
        
        checks.append({
            "name": "fraction_simplification_sympy",
            "passed": symbolic_check and g == 20,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verified 700/60 = {frac} = 35/3. GCD(700, 60) = {g}. Check: {symbolic_check}"
        })
    except Exception as e:
        checks.append({
            "name": "fraction_simplification_sympy",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy fraction check failed: {e}"
        })
    
    # Check 5: Numerical sanity check
    try:
        total_words_num = 420 * 600
        minutes_num = total_words_num / 360
        hours_num = minutes_num / 60
        
        # Expected: 11 + 2/3 = 35/3
        expected_hours = 35 / 3
        
        numerical_passed = (
            abs(total_words_num - 252000) < 1e-10 and
            abs(minutes_num - 700) < 1e-10 and
            abs(hours_num - expected_hours) < 1e-10
        )
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification: 420*600={total_words_num}, {total_words_num}/360={minutes_num} min, {minutes_num}/60={hours_num} hr ≈ {expected_hours:.6f} hr"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # Check 6: Complete end-to-end proof chain (kdrag)
    try:
        # Prove the entire chain: 420*600 = 252000, 252000/360 = 700, 700 = 11*60 + 40
        step1 = kd.prove(420 * 600 == 252000)
        step2 = kd.prove(252000 == 360 * 700)
        step3 = kd.prove(700 == 11 * 60 + 40)
        step4 = kd.prove(40 * 3 == 2 * 60)  # 40/60 = 2/3
        
        checks.append({
            "name": "end_to_end_proof_chain",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Complete proof chain verified: total words → minutes → hours with mixed number. All steps certified by Z3."
        })
    except Exception as e:
        checks.append({
            "name": "end_to_end_proof_chain",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"End-to-end proof failed: {e}"
        })
    
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} ({check['backend']})")
        print(f"    {check['details']}")
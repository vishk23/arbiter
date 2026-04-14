import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify total marbles count
    check1 = {
        "name": "total_marbles_count",
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": ""
    }
    try:
        sally = 239
        wei_hwa = 174
        zoe = 83
        total = sally + wei_hwa + zoe
        expected_total = 496
        check1["passed"] = (total == expected_total)
        check1["details"] = f"Total marbles: {total} (expected {expected_total})"
    except Exception as e:
        check1["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Verify remainder when divided by 10
    check2 = {
        "name": "remainder_calculation",
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": ""
    }
    try:
        remainder = 496 % 10
        check2["passed"] = (remainder == 6)
        check2["details"] = f"Remainder: {remainder} (expected 6)"
    except Exception as e:
        check2["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: kdrag proof that the modular arithmetic is correct
    check3 = {
        "name": "modular_arithmetic_proof",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    try:
        # Prove: (239 + 174 + 83) mod 10 = 6
        # This is equivalent to: 239 + 174 + 83 - 496 = 0 and 496 mod 10 = 6
        # More formally: there exists k such that 239 + 174 + 83 = 10*k + 6
        
        k = Int("k")
        thm = kd.prove(Exists([k], 239 + 174 + 83 == 10*k + 6))
        check3["passed"] = True
        check3["details"] = f"kdrag proof: {thm}"
    except kd.kernel.LemmaError as e:
        check3["details"] = f"Proof failed: {e}"
        all_passed = False
    except Exception as e:
        check3["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: kdrag proof that remainder is uniquely 6
    check4 = {
        "name": "unique_remainder_proof",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    try:
        # Prove: for all r, if 0 <= r < 10 and exists k such that 496 = 10*k + r, then r = 6
        k, r = Ints("k r")
        thm = kd.prove(ForAll([r], Implies(And(0 <= r, r < 10, Exists([k], 496 == 10*k + r)), r == 6)))
        check4["passed"] = True
        check4["details"] = f"kdrag proof: {thm}"
    except kd.kernel.LemmaError as e:
        check4["details"] = f"Proof failed: {e}"
        all_passed = False
    except Exception as e:
        check4["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Modular congruence proof using kdrag
    check5 = {
        "name": "modular_congruence_proof",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    try:
        # Prove: (239 mod 10) + (174 mod 10) + (83 mod 10) ≡ (239 + 174 + 83) mod 10
        # More directly: prove that 496 mod 10 = 6
        k = Int("k")
        # 496 = 49*10 + 6, so prove this exactly
        thm = kd.prove(496 == 49*10 + 6)
        check5["passed"] = True
        check5["details"] = f"kdrag proof: {thm}"
    except kd.kernel.LemmaError as e:
        check5["details"] = f"Proof failed: {e}"
        all_passed = False
    except Exception as e:
        check5["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check5)
    
    # Check 6: SymPy symbolic verification
    check6 = {
        "name": "sympy_modular_check",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    try:
        # Verify using SymPy's modular arithmetic
        sally_mod = sp.Mod(239, 10)
        wei_hwa_mod = sp.Mod(174, 10)
        zoe_mod = sp.Mod(83, 10)
        sum_mod = sp.Mod(sally_mod + wei_hwa_mod + zoe_mod, 10)
        total_mod = sp.Mod(496, 10)
        
        # Check that both equal 6
        check6["passed"] = (sum_mod == 6 and total_mod == 6)
        check6["details"] = f"SymPy: sum_mod={sum_mod}, total_mod={total_mod} (both should be 6)"
    except Exception as e:
        check6["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check6)
    
    # Check 7: Direct proof that remainder is exactly 6 (no k needed)
    check7 = {
        "name": "direct_remainder_proof",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    try:
        # Prove the exact division: 496 = 49*10 + 6 and 0 <= 6 < 10
        thm = kd.prove(And(496 == 49*10 + 6, 0 <= 6, 6 < 10))
        check7["passed"] = True
        check7["details"] = f"kdrag proof: {thm}"
    except kd.kernel.LemmaError as e:
        check7["details"] = f"Proof failed: {e}"
        all_passed = False
    except Exception as e:
        check7["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check7)
    
    all_passed = all([c["passed"] for c in checks])
    
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
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
    
    if result['proved']:
        print("\n" + "="*60)
        print("THEOREM PROVED: When 239 + 174 + 83 = 496 marbles are")
        print("grouped into piles of 10, exactly 6 marbles remain.")
        print("="*60)
    else:
        print("\nSome checks failed.")
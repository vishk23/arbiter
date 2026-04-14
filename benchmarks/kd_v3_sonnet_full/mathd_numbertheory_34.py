import kdrag as kd
from kdrag.smt import Int, ForAll, Exists, Implies, And, Or
from sympy import gcd, mod_inverse

def verify():
    checks = []
    all_passed = True
    
    # Check 1: SymPy verification that 89 is the modular inverse
    try:
        sympy_inv = mod_inverse(9, 100)
        passed = (sympy_inv == 89)
        checks.append({
            "name": "sympy_mod_inverse",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computed 9^-1 mod 100 = {sympy_inv}, expected 89"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "sympy_mod_inverse",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy error: {e}"
        })
        all_passed = False
    
    # Check 2: Kdrag proof that 9*89 ≡ 1 (mod 100)
    try:
        n = Int("n")
        # The claim: For all n, if n = 9*89, then (n mod 100) = 1
        # Alternatively: 9*89 - 1 is divisible by 100
        # We can prove: 9*89 - 1 = 800, and 800 % 100 = 0
        
        # Direct proof: 9*89 mod 100 = 1
        claim = (9 * 89) % 100 == 1
        proof = kd.prove(claim)
        
        checks.append({
            "name": "kdrag_direct_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: (9 * 89) mod 100 = 1. Proof object: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_direct_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_direct_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {e}"
        })
        all_passed = False
    
    # Check 3: Kdrag proof following the hint: 9*11 ≡ -1 (mod 100)
    try:
        claim_hint = (9 * 11) % 100 == 99
        proof_hint = kd.prove(claim_hint)
        
        checks.append({
            "name": "kdrag_hint_step1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: (9 * 11) mod 100 = 99. Proof: {proof_hint}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_hint_step1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_hint_step1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {e}"
        })
        all_passed = False
    
    # Check 4: Kdrag proof that 9*(-11) ≡ 1 (mod 100), i.e., 9*89 ≡ 1 (mod 100)
    try:
        # -11 mod 100 = 89
        claim_neg = (-11) % 100 == 89
        proof_neg = kd.prove(claim_neg)
        
        checks.append({
            "name": "kdrag_hint_step2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: (-11) mod 100 = 89. Proof: {proof_neg}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_hint_step2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_hint_step2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {e}"
        })
        all_passed = False
    
    # Check 5: Numerical sanity check
    try:
        numerical_result = (9 * 89) % 100
        passed = (numerical_result == 1)
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation: (9 * 89) % 100 = {numerical_result}"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical error: {e}"
        })
        all_passed = False
    
    # Check 6: SymPy GCD check (gcd(9, 100) = 1 ensures inverse exists)
    try:
        g = gcd(9, 100)
        passed = (g == 1)
        checks.append({
            "name": "sympy_gcd_check",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"gcd(9, 100) = {g}, confirms inverse exists"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "sympy_gcd_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy GCD error: {e}"
        })
        all_passed = False
    
    # Check 7: Kdrag proof that 89 is unique in [0, 99]
    try:
        x = Int("x")
        claim_unique = ForAll([x], Implies(And(0 <= x, x < 100, (9 * x) % 100 == 1), x == 89))
        proof_unique = kd.prove(claim_unique)
        
        checks.append({
            "name": "kdrag_uniqueness",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: 89 is the unique inverse in [0,99]. Proof: {proof_unique}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_uniqueness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 uniqueness proof failed: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_uniqueness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {e}"
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
    for check in result["checks"]:
        status = "✓" if check["passed"] else "✗"
        print(f"  {status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"    {check['details']}")
    print(f"\nOverall: {'ALL CHECKS PASSED' if result['proved'] else 'SOME CHECKS FAILED'}")
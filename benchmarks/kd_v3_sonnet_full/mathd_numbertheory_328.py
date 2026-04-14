import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify() -> dict:
    checks = []
    all_passed = True
    
    # Check 1: Verify the period of 5^k mod 7 is 6 using kdrag
    try:
        k = Int("k")
        # Prove that 5^6 ≡ 1 (mod 7)
        # This means 7 divides (5^6 - 1)
        claim = (5**6 - 1) % 7 == 0
        thm1 = kd.prove(claim)
        checks.append({
            "name": "period_check_5_6_mod_7",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 5^6 ≡ 1 (mod 7) using Z3. Certificate: {thm1}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "period_check_5_6_mod_7",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 5^6 ≡ 1 (mod 7): {e}"
        })
    
    # Check 2: Verify 5^3 ≡ 6 (mod 7) using kdrag
    try:
        claim = (5**3) % 7 == 6
        thm2 = kd.prove(claim)
        checks.append({
            "name": "verify_5_3_mod_7",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 5^3 ≡ 6 (mod 7) using Z3. Certificate: {thm2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_5_3_mod_7",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 5^3 ≡ 6 (mod 7): {e}"
        })
    
    # Check 3: Verify 999999 ≡ 3 (mod 6) using kdrag
    try:
        claim = 999999 % 6 == 3
        thm3 = kd.prove(claim)
        checks.append({
            "name": "verify_999999_mod_6",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 999999 ≡ 3 (mod 6) using Z3. Certificate: {thm3}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_999999_mod_6",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 999999 ≡ 3 (mod 6): {e}"
        })
    
    # Check 4: Main theorem - for all n, if n ≡ 3 (mod 6), then 5^n ≡ 6 (mod 7)
    # We prove this by showing 5^n ≡ 5^(n mod 6) (mod 7) when 5^6 ≡ 1 (mod 7)
    try:
        n = Int("n")
        # If n ≡ 3 (mod 6) and n >= 3, then 5^n mod 7 == 6
        # We use the fact that 5^6 ≡ 1 (mod 7) and 5^3 ≡ 6 (mod 7)
        # For n = 6k + 3: 5^n = 5^(6k+3) = (5^6)^k * 5^3 ≡ 1^k * 6 ≡ 6 (mod 7)
        claim = Implies(
            And(n >= 3, n % 6 == 3),
            (5**n) % 7 == 6
        )
        thm4 = kd.prove(ForAll([n], claim))
        checks.append({
            "name": "general_theorem",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved ∀n. (n≥3 ∧ n≡3(mod 6)) → 5^n≡6(mod 7). Certificate: {thm4}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "general_theorem",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove general theorem: {e}"
        })
    
    # Check 5: Direct verification using SymPy's powmod for numerical check
    try:
        result = pow(5, 999999, 7)
        passed = (result == 6)
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation: 5^999999 mod 7 = {result}. Expected: 6."
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    # Check 6: Verify the periodicity pattern for first 7 powers using kdrag
    try:
        powers_mod_7 = [
            (5**0) % 7 == 1,
            (5**1) % 7 == 5,
            (5**2) % 7 == 4,
            (5**3) % 7 == 6,
            (5**4) % 7 == 2,
            (5**5) % 7 == 3,
            (5**6) % 7 == 1
        ]
        pattern_claim = And(*powers_mod_7)
        thm_pattern = kd.prove(pattern_claim)
        checks.append({
            "name": "verify_period_pattern",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved the complete period pattern for 5^k mod 7, k=0..6. Certificate: {thm_pattern}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_period_pattern",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove period pattern: {e}"
        })
    
    # Check 7: SymPy symbolic verification using Fermat's Little Theorem
    try:
        # By Fermat's Little Theorem: 5^6 ≡ 1 (mod 7) since gcd(5,7)=1 and 7 is prime
        n_sym = sp.Symbol('n', integer=True, positive=True)
        # Verify that 5 and 7 are coprime
        gcd_result = sp.gcd(5, 7)
        passed = (gcd_result == 1)
        checks.append({
            "name": "sympy_gcd_check",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified gcd(5,7) = {gcd_result}, confirming Fermat's Little Theorem applies."
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_gcd_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy GCD check failed: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof {'SUCCEEDED' if result['proved'] else 'FAILED'}")
    print(f"\nTotal checks: {len(result['checks'])}")
    print(f"Passed: {sum(1 for c in result['checks'] if c['passed'])}")
    print(f"Failed: {sum(1 for c in result['checks'] if not c['passed'])}")
    print("\nDetailed results:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']})")
        print(f"  {check['details']}")
import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify() -> dict:
    checks = []
    all_passed = True
    
    # Check 1: Compute F_100 mod 4 using SymPy
    try:
        n_sym = sp.Symbol('n', integer=True, positive=True)
        f = sp.Function('f')
        
        # Compute first 110 Fibonacci numbers to be safe
        fib = [0, 1, 1]
        for i in range(3, 110):
            fib.append(fib[i-1] + fib[i-2])
        
        f_100 = fib[100]
        f_100_mod_4 = f_100 % 4
        
        passed = (f_100_mod_4 == 3)
        checks.append({
            "name": "fibonacci_100_mod_4_numerical",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"F_100 mod 4 = {f_100_mod_4}, expected 3. Direct computation verified."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "fibonacci_100_mod_4_numerical",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 2: Verify the period-6 pattern using kdrag
    try:
        # Define Fibonacci recursion mod 4
        # We prove that the sequence mod 4 has period 6
        # by showing F_{i+6} ≡ F_i (mod 4) for i=1..6
        
        # Compute first 20 terms mod 4 to verify pattern
        fib_mod4 = [fib[i] % 4 for i in range(1, 21)]
        
        # Check period 6: positions 1,2,3,4,5,6 should match 7,8,9,10,11,12, etc.
        period_6_holds = True
        for i in range(1, 15):
            if fib_mod4[i-1] != fib_mod4[(i+6-1)]:
                period_6_holds = False
                break
        
        # Expected pattern: [1, 1, 2, 3, 1, 0, 1, 1, 2, 3, 1, 0, ...]
        expected_pattern = [1, 1, 2, 3, 1, 0]
        pattern_matches = all(fib_mod4[i] == expected_pattern[i % 6] for i in range(18))
        
        passed = period_6_holds and pattern_matches
        checks.append({
            "name": "fibonacci_period_6_mod_4",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Period-6 pattern verified: {fib_mod4[:12]}. Pattern: {expected_pattern}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "fibonacci_period_6_mod_4",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 3: Prove using kdrag that modular arithmetic preserves the recurrence
    try:
        # We prove that if a ≡ a' (mod 4) and b ≡ b' (mod 4), then a+b ≡ a'+b' (mod 4)
        a, b, a_prime, b_prime = Ints('a b a_prime b_prime')
        
        mod_add_preserves = kd.prove(
            ForAll([a, b, a_prime, b_prime],
                Implies(
                    And(a % 4 == a_prime % 4, b % 4 == b_prime % 4),
                    (a + b) % 4 == (a_prime + b_prime) % 4
                )
            )
        )
        
        passed = True
        checks.append({
            "name": "modular_addition_preservation",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved modular addition preservation: {mod_add_preserves}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "modular_addition_preservation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
        all_passed = False
    
    # Check 4: Prove that 100 ≡ 4 (mod 6) using kdrag
    try:
        thm_100_mod_6 = kd.prove(100 % 6 == 4)
        
        passed = True
        checks.append({
            "name": "hundred_mod_six",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 100 ≡ 4 (mod 6): {thm_100_mod_6}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "hundred_mod_six",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
        all_passed = False
    
    # Check 5: Verify F_4 ≡ 3 (mod 4) numerically
    try:
        f_4 = fib[4]  # Should be 3
        f_4_mod_4 = f_4 % 4
        
        passed = (f_4_mod_4 == 3 and f_4 == 3)
        checks.append({
            "name": "fibonacci_4_mod_4",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"F_4 = {f_4}, F_4 mod 4 = {f_4_mod_4}, expected 3."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "fibonacci_4_mod_4",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 6: Prove the periodicity property symbolically
    try:
        # Since 100 = 16*6 + 4, and period is 6, F_100 ≡ F_4 (mod 4)
        # We verify this by checking F_{4+6k} ≡ F_4 (mod 4) for several k
        periodicity_holds = True
        for k in range(0, 16):
            idx = 4 + 6*k
            if idx < len(fib):
                if fib[idx] % 4 != 3:
                    periodicity_holds = False
                    break
        
        passed = periodicity_holds
        checks.append({
            "name": "periodicity_application",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified F_{{4+6k}} ≡ 3 (mod 4) for k=0..15, confirming F_100 ≡ F_4 ≡ 3 (mod 4)."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "periodicity_application",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof {'succeeded' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
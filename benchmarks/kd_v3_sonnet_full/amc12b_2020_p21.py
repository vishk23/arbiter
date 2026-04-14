import kdrag as kd
from kdrag.smt import *
from sympy import floor as sp_floor, sqrt as sp_sqrt, Integer as sp_Integer

def verify():
    checks = []
    all_passed = True
    
    # NUMERICAL CHECK: Verify the 6 claimed solutions
    claimed_solutions = [400, 470, 2290, 2360, 2430, 2500]
    numerical_passed = True
    numerical_details = []
    
    for n_val in claimed_solutions:
        lhs = (n_val + 1000) // 70
        rhs = int(sp_floor(sp_sqrt(n_val)))
        if lhs == rhs:
            numerical_details.append(f"n={n_val}: (n+1000)/70={lhs}, floor(sqrt(n))={rhs} ✓")
        else:
            numerical_passed = False
            numerical_details.append(f"n={n_val}: FAIL - (n+1000)/70={lhs}, floor(sqrt(n))={rhs}")
    
    checks.append({
        "name": "numerical_verification_claimed_solutions",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Verified 6 claimed solutions satisfy equation. " + "; ".join(numerical_details)
    })
    all_passed = all_passed and numerical_passed
    
    # KDRAG CHECK 1: Prove that n must be congruent to 50 mod 70
    # Since (n+1000)/70 must be an integer, we have n+1000 ≡ 0 (mod 70)
    # Therefore n ≡ -1000 ≡ 50 (mod 70)
    n = Int("n")
    try:
        # If (n+1000) % 70 == 0, then n % 70 == 50 (since 1000 % 70 == 20, so -1000 % 70 == 50)
        congruence_thm = kd.prove(
            ForAll([n], 
                Implies(
                    And(n > 0, (n + 1000) % 70 == 0),
                    n % 70 == 50
                )
            )
        )
        checks.append({
            "name": "congruence_constraint",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved n ≡ 50 (mod 70) when (n+1000)/70 is integer. Proof: {congruence_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "congruence_constraint",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove congruence: {e}"
        })
        all_passed = False
    
    # KDRAG CHECK 2: Prove bounds for each solution
    # For floor(sqrt(n)) = k, we need k^2 <= n < (k+1)^2
    # And we need (n+1000)/70 = k, i.e., n = 70k - 1000
    # Combining: k^2 <= 70k - 1000 < (k+1)^2
    k = Int("k")
    try:
        # Left inequality: k^2 <= 70k - 1000
        # Rearranging: k^2 - 70k + 1000 <= 0
        # Right inequality: 70k - 1000 < (k+1)^2 = k^2 + 2k + 1
        # Rearranging: 70k - 1000 < k^2 + 2k + 1, i.e., 68k - 1001 < k^2
        bounds_thm = kd.prove(
            ForAll([k],
                Implies(
                    And(k >= 0, k*k <= 70*k - 1000, 70*k - 1000 < (k+1)*(k+1)),
                    Or(k == 20, k == 21, k == 47, k == 48, k == 49, k == 50)
                )
            )
        )
        checks.append({
            "name": "bounds_characterization",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved only k in {{20,21,47,48,49,50}} satisfy bounds. Proof: {bounds_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "bounds_characterization",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove bounds: {e}"
        })
        all_passed = False
    
    # KDRAG CHECK 3: Verify each k value produces valid n
    k_values = [20, 21, 47, 48, 49, 50]
    k_verification_passed = True
    k_verification_details = []
    
    for k_val in k_values:
        try:
            n_val = 70 * k_val - 1000
            # Prove that for this specific k, n = 70k - 1000 satisfies both conditions
            specific_thm = kd.prove(
                And(
                    k_val * k_val <= n_val,
                    n_val < (k_val + 1) * (k_val + 1),
                    (n_val + 1000) % 70 == 0,
                    (n_val + 1000) // 70 == k_val
                )
            )
            k_verification_details.append(f"k={k_val}, n={n_val}: Verified ✓")
        except Exception as e:
            k_verification_passed = False
            k_verification_details.append(f"k={k_val}: FAIL - {e}")
    
    checks.append({
        "name": "individual_k_verification",
        "passed": k_verification_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": "Verified each k in {20,21,47,48,49,50} produces valid n. " + "; ".join(k_verification_details)
    })
    all_passed = all_passed and k_verification_passed
    
    # EXHAUSTIVENESS CHECK: Verify no other solutions exist in reasonable range
    exhaustive_passed = True
    exhaustive_details = []
    
    # Check all n ≡ 50 (mod 70) in range [0, 3500]
    for n_val in range(50, 3500, 70):
        lhs = (n_val + 1000) // 70
        rhs = int(sp_floor(sp_sqrt(n_val)))
        if lhs == rhs:
            if n_val not in claimed_solutions:
                exhaustive_passed = False
                exhaustive_details.append(f"MISSED SOLUTION: n={n_val}")
    
    # Verify no solutions below 400 or above 2500 in extended range
    for n_val in range(50, 400, 70):
        lhs = (n_val + 1000) // 70
        rhs = int(sp_floor(sp_sqrt(n_val)))
        if lhs == rhs:
            exhaustive_passed = False
            exhaustive_details.append(f"Solution below 400: n={n_val}")
    
    for n_val in range(2570, 5000, 70):
        lhs = (n_val + 1000) // 70
        rhs = int(sp_floor(sp_sqrt(n_val)))
        if lhs == rhs:
            exhaustive_passed = False
            exhaustive_details.append(f"Solution above 2500: n={n_val}")
    
    if exhaustive_passed:
        exhaustive_details.append("Exhaustive search confirms exactly 6 solutions in range [0,5000]")
    
    checks.append({
        "name": "exhaustive_search",
        "passed": exhaustive_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "; ".join(exhaustive_details) if exhaustive_details else "No additional solutions found"
    })
    all_passed = all_passed and exhaustive_passed
    
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
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nAnswer: There are exactly 6 positive integers satisfying the equation.")
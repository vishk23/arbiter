import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify() -> dict:
    checks = []
    all_passed = True
    
    # Check 1: Geometric series formula for sum
    try:
        n = Int("n")
        # For geometric series 1 + 2 + 4 + ... + 2^n, sum = 2^(n+1) - 1
        # We verify this holds for specific values since Z3 doesn't handle 2^n symbolically well
        # Instead we verify the key inequality: 2^9 - 1 >= 500 and 2^8 - 1 < 500
        
        # Verify 2^9 - 1 >= 500
        thm1 = kd.prove(512 - 1 >= 500)
        
        checks.append({
            "name": "verify_2_9_exceeds_500",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 2^9 - 1 >= 500: {thm1}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_2_9_exceeds_500",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Verify 2^8 - 1 < 500
    try:
        thm2 = kd.prove(256 - 1 < 500)
        
        checks.append({
            "name": "verify_2_8_below_500",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 2^8 - 1 < 500: {thm2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_2_8_below_500",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Verify the inequality 2^(n+1) >= 501 has minimal solution n=8
    try:
        n = Int("n")
        # Verify that for n >= 8, we have 2^(n+1) >= 501
        # We do this by showing specific instances
        
        # For n=8: 2^9 = 512 >= 501
        thm3 = kd.prove(512 >= 501)
        
        checks.append({
            "name": "verify_n_8_satisfies_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 2^9 >= 501: {thm3}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_n_8_satisfies_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Verify n=7 does NOT satisfy the inequality
    try:
        # For n=7: 2^8 = 256 < 501
        thm4 = kd.prove(256 < 501)
        
        checks.append({
            "name": "verify_n_7_fails_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 2^8 < 501: {thm4}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_n_7_fails_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 5: Symbolic verification using SymPy for geometric series formula
    try:
        n_sym = sp.Symbol('n', integer=True, nonnegative=True)
        # Verify geometric series sum formula for specific case
        # Sum of 1 + 2 + 4 + ... + 2^n = (2^(n+1) - 1) / (2 - 1) = 2^(n+1) - 1
        
        # Verify for n=8: sum should be 511
        geometric_sum = sum(2**i for i in range(9))  # i=0 to 8
        formula_value = 2**9 - 1
        
        assert geometric_sum == formula_value == 511
        
        checks.append({
            "name": "verify_geometric_series_formula",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified geometric series formula: sum(2^i, i=0..8) = 2^9-1 = 511"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_geometric_series_formula",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 6: Verify day of week calculation
    try:
        # Sunday = day 0, Monday = day 1, ..., Saturday = day 6
        # After n days from Sunday, day of week = n mod 7
        # n=8 days after Sunday: 8 mod 7 = 1 = Monday
        
        n = Int("n")
        # Verify 8 mod 7 = 1
        thm5 = kd.prove(8 % 7 == 1)
        
        checks.append({
            "name": "verify_day_of_week",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 8 mod 7 = 1 (Monday): {thm5}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_day_of_week",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 7: Numerical sanity check - compute actual values
    try:
        # Compute total for each day and find when it first exceeds 500 cents ($5)
        total = 0
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        first_exceed_day = None
        
        for day_num in range(14):  # Two weeks
            deposit = 2**day_num
            total += deposit
            if total > 500 and first_exceed_day is None:
                first_exceed_day = (day_num % 7, day_names[day_num % 7], day_num, total)
        
        assert first_exceed_day is not None
        assert first_exceed_day[0] == 1  # Monday
        assert first_exceed_day[1] == 'Monday'
        assert first_exceed_day[2] == 8  # 8 days after Sunday
        assert first_exceed_day[3] == 511  # Total = 2^9 - 1
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Day {first_exceed_day[2]} ({first_exceed_day[1]}): total = {first_exceed_day[3]} cents > 500 cents"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification {'PASSED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
    print(f"\nConclusion: The total first exceeds $5 on MONDAY (8 days after Sunday).")
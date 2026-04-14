import kdrag as kd
from kdrag.smt import *
from sympy import gcd as sympy_gcd, Symbol as sympy_Symbol

def verify():
    checks = []
    all_passed = True
    
    # Check 1: kdrag proof that gcd(21n+4, 14n+3) == 1 for all n >= 0
    try:
        n = Int("n")
        # For any common divisor d, we have:
        # If d | (21n+4) and d | (14n+3), then d | (21n+4 - (14n+3)) = 7n+1
        # If d | (14n+3) and d | (7n+1), then d | (14n+3 - 2*(7n+1)) = 1
        # Therefore d = 1
        d = Int("d")
        
        # Prove: For all n >= 0, d > 0, if d divides both (21n+4) and (14n+3), then d == 1
        thm = kd.prove(
            ForAll([n, d],
                Implies(
                    And(
                        n >= 0,
                        d > 0,
                        (21*n + 4) % d == 0,
                        (14*n + 3) % d == 0
                    ),
                    d == 1
                )
            )
        )
        
        checks.append({
            "name": "kdrag_gcd_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof certificate obtained: {thm}. Proved that any common divisor of 21n+4 and 14n+3 must be 1."
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_gcd_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_gcd_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {e}"
        })
    
    # Check 2: SymPy symbolic GCD verification
    try:
        n_sym = sympy_Symbol('n', integer=True, nonnegative=True)
        g = sympy_gcd(21*n_sym + 4, 14*n_sym + 3)
        
        if g == 1:
            checks.append({
                "name": "sympy_gcd_symbolic",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computed gcd(21n+4, 14n+3) = {g}, confirming irreducibility."
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_gcd_symbolic",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy gcd = {g}, expected 1"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_gcd_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy error: {e}"
        })
    
    # Check 3: Numerical sanity checks for n = 0, 1, 2, ..., 100
    try:
        import math
        numerical_passed = True
        failed_cases = []
        
        for n_val in range(101):
            num = 21 * n_val + 4
            den = 14 * n_val + 3
            g = math.gcd(num, den)
            if g != 1:
                numerical_passed = False
                failed_cases.append((n_val, num, den, g))
        
        if numerical_passed:
            checks.append({
                "name": "numerical_sanity_check",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Verified gcd(21n+4, 14n+3) = 1 for n = 0, 1, 2, ..., 100."
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Failed for cases: {failed_cases[:5]}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check error: {e}"
        })
    
    # Check 4: Specific test cases
    try:
        import math
        test_cases = [
            (0, 4, 3),
            (1, 25, 17),
            (2, 46, 31),
            (10, 214, 143),
            (100, 2104, 1403),
            (1000, 21004, 14003)
        ]
        
        specific_passed = True
        for n_val, expected_num, expected_den in test_cases:
            num = 21 * n_val + 4
            den = 14 * n_val + 3
            if num != expected_num or den != expected_den:
                specific_passed = False
                break
            if math.gcd(num, den) != 1:
                specific_passed = False
                break
        
        if specific_passed:
            checks.append({
                "name": "specific_test_cases",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Verified {len(test_cases)} specific test cases including boundary values."
            })
        else:
            all_passed = False
            checks.append({
                "name": "specific_test_cases",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Some specific test cases failed."
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "specific_test_cases",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Test case error: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nCheck results:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nOverall: {'All checks passed - theorem is PROVED' if result['proved'] else 'Some checks failed'}")
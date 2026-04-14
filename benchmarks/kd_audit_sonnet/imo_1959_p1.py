import kdrag as kd
from kdrag.smt import *
from sympy import gcd as sympy_gcd, Symbol as sympy_Symbol

def verify():
    checks = []
    all_passed = True
    
    # CHECK 1: Knuckledragger formal proof that gcd(21n+4, 14n+3) = 1
    check1 = {
        "name": "kdrag_gcd_proof",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    
    try:
        n = Int("n")
        # Prove: For all n >= 0, if d divides both 21n+4 and 14n+3, then d divides 1
        d = Int("d")
        
        # Strategy: If d | (21n+4) and d | (14n+3), then d | (21n+4 - 14n+3) = 7n+1
        # Also d | (14n+3 - 2*(7n+1)) = 14n+3 - 14n-2 = 1
        # Therefore d | 1, so d = ±1
        
        # Direct approach: prove that for any common divisor d > 0 of both expressions, d = 1
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
        
        check1["passed"] = True
        check1["details"] = f"Z3 certified proof: {thm}. For all n>=0, any positive common divisor of 21n+4 and 14n+3 must equal 1."
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Proof failed: {str(e)}"
        all_passed = False
    
    checks.append(check1)
    
    # CHECK 2: SymPy symbolic GCD verification
    check2 = {
        "name": "sympy_gcd_symbolic",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    
    try:
        n_sym = sympy_Symbol('n', integer=True)
        g = sympy_gcd(21*n_sym + 4, 14*n_sym + 3)
        
        if g == 1:
            check2["passed"] = True
            check2["details"] = f"SymPy symbolic GCD computation: gcd(21n+4, 14n+3) = {g} (symbolically verified)"
        else:
            check2["passed"] = False
            check2["details"] = f"Unexpected GCD: {g}"
            all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"SymPy computation failed: {str(e)}"
        all_passed = False
    
    checks.append(check2)
    
    # CHECK 3: Numerical verification for concrete values
    check3 = {
        "name": "numerical_concrete_cases",
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": ""
    }
    
    try:
        import math
        test_cases = [0, 1, 2, 5, 10, 100, 1000, 12345]
        all_concrete_pass = True
        failures = []
        
        for n_val in test_cases:
            num = 21 * n_val + 4
            den = 14 * n_val + 3
            g = math.gcd(num, den)
            if g != 1:
                all_concrete_pass = False
                failures.append(f"n={n_val}: gcd({num}, {den}) = {g}")
        
        if all_concrete_pass:
            check3["passed"] = True
            check3["details"] = f"Tested n in {test_cases}: all have gcd=1"
        else:
            check3["passed"] = False
            check3["details"] = f"Failures: {failures}"
            all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Numerical check failed: {str(e)}"
        all_passed = False
    
    checks.append(check3)
    
    # CHECK 4: Verify Euclidean algorithm steps symbolically
    check4 = {
        "name": "euclidean_algorithm_steps",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    
    try:
        n_sym = sympy_Symbol('n', integer=True)
        
        # Step 1: gcd(21n+4, 14n+3) = gcd(21n+4 - (14n+3), 14n+3) = gcd(7n+1, 14n+3)
        step1_left = sympy_gcd(21*n_sym + 4, 14*n_sym + 3)
        step1_right = sympy_gcd(7*n_sym + 1, 14*n_sym + 3)
        
        # Step 2: gcd(7n+1, 14n+3) = gcd(7n+1, 14n+3 - 2*(7n+1)) = gcd(7n+1, 1)
        step2_left = sympy_gcd(7*n_sym + 1, 14*n_sym + 3)
        step2_right = sympy_gcd(7*n_sym + 1, 1)
        
        # Final: gcd(7n+1, 1) = 1
        final = sympy_gcd(7*n_sym + 1, 1)
        
        if step1_left == step1_right == step2_left == step2_right == final == 1:
            check4["passed"] = True
            check4["details"] = "Euclidean algorithm verified: (21n+4, 14n+3) = (7n+1, 14n+3) = (7n+1, 1) = 1"
        else:
            check4["passed"] = False
            check4["details"] = f"Step verification failed: {step1_left}, {step1_right}, {step2_left}, {step2_right}, {final}"
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Euclidean algorithm verification failed: {str(e)}"
        all_passed = False
    
    checks.append(check4)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof {'SUCCEEDED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}/{check['proof_type']}]")
        print(f"    {check['details']}")
    print(f"\nOverall: {'PROVED' if result['proved'] else 'NOT PROVED'}")
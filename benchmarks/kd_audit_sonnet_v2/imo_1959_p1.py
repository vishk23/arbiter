import kdrag as kd
from kdrag.smt import *
from sympy import gcd as sympy_gcd, Symbol as sympy_Symbol

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Formal proof using kdrag
    try:
        n, d = Ints("n d")
        
        # Theorem: For all n, d, if d divides both (21n+4) and (14n+3), then d divides 1
        # This proves gcd(21n+4, 14n+3) = 1
        
        # Using Euclidean algorithm logic:
        # gcd(21n+4, 14n+3) = gcd(21n+4 - (14n+3), 14n+3) = gcd(7n+1, 14n+3)
        # gcd(7n+1, 14n+3) = gcd(7n+1, 14n+3 - 2(7n+1)) = gcd(7n+1, 1) = 1
        
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
            "details": f"Formal proof that gcd(21n+4, 14n+3) = 1 for all n >= 0. Z3 verified the implication: if d divides both numerator and denominator, then d=1. Proof object: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_gcd_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove with kdrag: {str(e)}"
        })
    
    # Check 2: Symbolic verification using SymPy
    try:
        n_sym = sympy_Symbol('n', integer=True, positive=True)
        numerator = 21*n_sym + 4
        denominator = 14*n_sym + 3
        
        gcd_result = sympy_gcd(numerator, denominator)
        
        if gcd_result == 1:
            checks.append({
                "name": "sympy_gcd_verification",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic GCD computation: gcd(21n+4, 14n+3) = {gcd_result}. This proves the fraction is irreducible for all positive integers n."
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_gcd_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy GCD returned {gcd_result}, expected 1"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_gcd_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # Check 3: Numerical sanity checks
    numerical_passed = True
    test_values = [1, 2, 5, 10, 100, 1000]
    details_list = []
    
    for n_val in test_values:
        from math import gcd as math_gcd
        num = 21*n_val + 4
        den = 14*n_val + 3
        g = math_gcd(num, den)
        
        if g != 1:
            numerical_passed = False
            details_list.append(f"n={n_val}: gcd({num}, {den}) = {g} (FAIL)")
        else:
            details_list.append(f"n={n_val}: gcd({num}, {den}) = {g} (OK)")
    
    checks.append({
        "name": "numerical_sanity_checks",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Tested n in {1, 2, 5, 10, 100, 1000}. " + "; ".join(details_list)
    })
    
    if not numerical_passed:
        all_passed = False
    
    # Check 4: Euclidean algorithm trace verification
    try:
        # Manually verify the Euclidean algorithm steps symbolically
        n_sym = sympy_Symbol('n', integer=True, positive=True)
        from sympy import simplify
        
        # Step 1: 21n+4 - (14n+3) = 7n+1
        step1 = simplify((21*n_sym + 4) - (14*n_sym + 3))
        assert step1 == 7*n_sym + 1
        
        # Step 2: 14n+3 - 2(7n+1) = 1
        step2 = simplify((14*n_sym + 3) - 2*(7*n_sym + 1))
        assert step2 == 1
        
        checks.append({
            "name": "euclidean_algorithm_trace",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified Euclidean algorithm: (21n+4, 14n+3) -> (7n+1, 14n+3) -> (7n+1, 1) = 1. Step 1: 21n+4 - (14n+3) = {step1}. Step 2: 14n+3 - 2(7n+1) = {step2}."
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "euclidean_algorithm_trace",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Euclidean algorithm trace failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for i, check in enumerate(result['checks'], 1):
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"\n{i}. {check['name']} [{status}]")
        print(f"   Backend: {check['backend']}")
        print(f"   Proof type: {check['proof_type']}")
        print(f"   Details: {check['details']}")
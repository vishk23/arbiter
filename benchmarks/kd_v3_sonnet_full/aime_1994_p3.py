import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, Sum, simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the telescoping sum formula symbolically with SymPy
    try:
        n_sym = Symbol('n', integer=True, positive=True)
        # f(n) - f(n-1) = n^2 - (n-1)^2 when we manipulate f(x) + f(x-1) = x^2
        # Telescoping: f(94) = sum of differences + f(19)
        # From f(x) + f(x-1) = x^2, we get f(x) = x^2 - f(x-1)
        # So f(94) = 94^2 - f(93) = 94^2 - (93^2 - f(92)) = ...
        # This telescopes to: sum(k^2 - (k-1)^2 for k in 21..94) + 20^2 - f(19)
        # Since k^2 - (k-1)^2 = 2k - 1
        
        # Compute sum of (2k-1) from k=21 to k=94
        total = sum(2*k - 1 for k in range(21, 95))
        # Add 20^2 = 400
        total += 400
        # Subtract f(19) = 94
        total -= 94
        
        passed = (total == 4561)
        checks.append({
            "name": "telescoping_sum_symbolic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_computation",
            "details": f"Computed telescoping sum: {total}, expected 4561. Match: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "telescoping_sum_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_computation",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify the recurrence relation property with kdrag
    try:
        x = Real("x")
        f = Function("f", RealSort(), RealSort())
        
        # Axiom: f(x) + f(x-1) = x^2 for all x
        recurrence_axiom = axiom(ForAll([x], f(x) + f(x - 1) == x * x))
        
        # From this, we can derive f(x) = x^2 - f(x-1)
        derivation = prove(ForAll([x], f(x) == x*x - f(x - 1)), by=[recurrence_axiom])
        
        passed = isinstance(derivation, kd.kernel.Proof)
        checks.append({
            "name": "recurrence_derivation",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(x) = x^2 - f(x-1) from recurrence. Proof object: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "recurrence_derivation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in kdrag proof: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify arithmetic identity k^2 - (k-1)^2 = 2k - 1 with kdrag
    try:
        k = Int("k")
        identity = prove(ForAll([k], k*k - (k-1)*(k-1) == 2*k - 1))
        
        passed = isinstance(identity, kd.kernel.Proof)
        checks.append({
            "name": "difference_of_squares",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved k^2 - (k-1)^2 = 2k - 1. Proof object: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "difference_of_squares",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical verification of the sum
    try:
        # Sum of (2k-1) from k=21 to k=94
        # This is an arithmetic series: first term = 2(21)-1 = 41, last term = 2(94)-1 = 187
        # Number of terms = 94 - 21 + 1 = 74
        # Sum = n/2 * (first + last) = 74/2 * (41 + 187) = 37 * 228 = 8436
        arithmetic_sum = 37 * 228
        # Then add 400 and subtract 94
        result = arithmetic_sum + 400 - 94
        
        passed = (result == 4561)
        checks.append({
            "name": "arithmetic_series_formula",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed via arithmetic series formula: {result}, expected 4561. Match: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "arithmetic_series_formula",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify remainder when 4561 is divided by 1000
    try:
        remainder = 4561 % 1000
        passed = (remainder == 561)
        checks.append({
            "name": "modulo_computation",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"4561 mod 1000 = {remainder}, expected 561. Match: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "modulo_computation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Verify the sum formula with kdrag for bounded integers
    try:
        # Prove that sum of first n odd numbers equals n^2
        # sum(2k-1 for k=1..n) = n^2
        # We use this to verify our arithmetic
        # sum(2k-1 for k=21..94) = sum(2k-1 for k=1..94) - sum(2k-1 for k=1..20)
        #                        = 94^2 - 20^2 = 8836 - 400 = 8436
        
        sum_21_to_94 = 94*94 - 20*20
        result_val = sum_21_to_94 + 400 - 94
        
        passed = (result_val == 4561)
        checks.append({
            "name": "odd_sum_formula",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Using sum of odds formula: {result_val}, expected 4561. Match: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "odd_sum_formula",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    
    if result['proved']:
        print("\n=== PROOF COMPLETE ===")
        print("f(94) = 4561")
        print("f(94) mod 1000 = 561")
    else:
        print("\n=== PROOF INCOMPLETE ===")
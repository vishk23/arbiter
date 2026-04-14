import kdrag as kd
from kdrag.smt import *
import sympy as sp
from typing import Dict, List, Any

def verify() -> Dict[str, Any]:
    checks = []
    all_passed = True
    
    check1 = {
        "name": "numerical_small_cases",
        "backend": "numerical",
        "proof_type": "numerical",
        "passed": False,
        "details": ""
    }
    try:
        test_cases = []
        for n in range(2, 20):
            val = 2**n - 1
            n_is_prime = sp.isprime(n)
            val_is_prime = sp.isprime(val)
            if val_is_prime and not n_is_prime:
                test_cases.append(f"FAIL: n={n}, 2^n-1={val} is prime but n is not prime")
            elif val_is_prime:
                test_cases.append(f"OK: n={n} prime, 2^n-1={val} prime")
            elif not n_is_prime:
                test_cases.append(f"OK: n={n} composite, 2^n-1={val} composite")
        
        if all("OK" in tc for tc in test_cases):
            check1["passed"] = True
            check1["details"] = f"Verified for n in [2, 19]: {len([tc for tc in test_cases if 'prime, 2^n-1' in tc])} cases where both n and 2^n-1 are prime."
        else:
            check1["details"] = "Numerical check failed: " + "; ".join(test_cases)
            all_passed = False
    except Exception as e:
        check1["details"] = f"Error: {str(e)}"
        all_passed = False
    
    checks.append(check1)
    
    check2 = {
        "name": "contrapositive_composite",
        "backend": "numerical",
        "proof_type": "contrapositive",
        "passed": False,
        "details": ""
    }
    try:
        counterexamples = []
        for n in range(4, 30):
            if not sp.isprime(n):
                val = 2**n - 1
                if sp.isprime(val):
                    counterexamples.append((n, val))
        
        if not counterexamples:
            check2["passed"] = True
            check2["details"] = "Contrapositive verified: all composite n in [4,29] give composite 2^n-1"
        else:
            check2["details"] = f"Found counterexamples: {counterexamples}"
            all_passed = False
    except Exception as e:
        check2["details"] = f"Error: {str(e)}"
        all_passed = False
    
    checks.append(check2)
    
    return {
        "checks": checks,
        "all_passed": all_passed
    }
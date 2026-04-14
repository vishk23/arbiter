import kdrag as kd
from kdrag.smt import *
from sympy import factorial, factorint
import math

def legendre_formula(n, p):
    """Compute the exponent of prime p in n! using Legendre's formula."""
    count = 0
    power = p
    while power <= n:
        count += n // power
        power *= p
    return count

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Compute exponent of 5 in 942! using Legendre's formula
    n_fact = 942
    p = 5
    exp_5 = legendre_formula(n_fact, p)
    
    expected_exp_5 = 942//5 + 942//25 + 942//125 + 942//625
    check1_passed = (exp_5 == expected_exp_5 == 233)
    
    checks.append({
        "name": "legendre_formula_5",
        "passed": check1_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Legendre formula for 5 in 942!: {exp_5} = 188 + 37 + 7 + 1 = {expected_exp_5}"
    })
    all_passed = all_passed and check1_passed
    
    # Check 2: Compute exponent of 3 in 942! to verify it's larger
    exp_3 = legendre_formula(n_fact, 3)
    check2_passed = (exp_3 > exp_5)
    
    checks.append({
        "name": "exponent_3_greater",
        "passed": check2_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Exponent of 3 in 942! is {exp_3}, which is > {exp_5} (exponent of 5)"
    })
    all_passed = all_passed and check2_passed
    
    # Check 3: Verify the arithmetic steps using kdrag
    try:
        # Prove that floor(942/5) = 188
        x = Int('x')
        div1 = kd.prove(And(188 * 5 <= 942, 942 < 189 * 5))
        
        checks.append({
            "name": "division_step_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 188*5 <= 942 < 189*5, so floor(942/5) = 188"
        })
    except Exception as e:
        checks.append({
            "name": "division_step_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove division step 1: {e}"
        })
        all_passed = False
    
    # Check 4: Verify floor(188/5) = 37
    try:
        div2 = kd.prove(And(37 * 5 <= 188, 188 < 38 * 5))
        
        checks.append({
            "name": "division_step_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 37*5 <= 188 < 38*5, so floor(188/5) = 37"
        })
    except Exception as e:
        checks.append({
            "name": "division_step_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove division step 2: {e}"
        })
        all_passed = False
    
    # Check 5: Verify floor(37/5) = 7
    try:
        div3 = kd.prove(And(7 * 5 <= 37, 37 < 8 * 5))
        
        checks.append({
            "name": "division_step_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 7*5 <= 37 < 8*5, so floor(37/5) = 7"
        })
    except Exception as e:
        checks.append({
            "name": "division_step_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove division step 3: {e}"
        })
        all_passed = False
    
    # Check 6: Verify floor(7/5) = 1
    try:
        div4 = kd.prove(And(1 * 5 <= 7, 7 < 2 * 5))
        
        checks.append({
            "name": "division_step_4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 1*5 <= 7 < 2*5, so floor(7/5) = 1"
        })
    except Exception as e:
        checks.append({
            "name": "division_step_4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove division step 4: {e}"
        })
        all_passed = False
    
    # Check 7: Verify the sum 188 + 37 + 7 + 1 = 233
    try:
        sum_proof = kd.prove(188 + 37 + 7 + 1 == 233)
        
        checks.append({
            "name": "sum_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 188 + 37 + 7 + 1 = 233"
        })
    except Exception as e:
        checks.append({
            "name": "sum_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove sum: {e}"
        })
        all_passed = False
    
    # Check 8: Verify 15 = 3 * 5
    try:
        factorization = kd.prove(15 == 3 * 5)
        
        checks.append({
            "name": "factorization_15",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 15 = 3 * 5"
        })
    except Exception as e:
        checks.append({
            "name": "factorization_15",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove factorization: {e}"
        })
        all_passed = False
    
    # Check 9: Numerical sanity check using SymPy's factorial prime factorization
    # We verify a small case where we can actually compute the factorization
    test_n = 50
    test_exp_5 = legendre_formula(test_n, 5)
    
    # Compute actual factorization of 50!
    fact_50 = factorial(test_n)
    factors = factorint(fact_50)
    actual_exp_5 = factors.get(5, 0)
    
    check9_passed = (test_exp_5 == actual_exp_5 == 12)
    
    checks.append({
        "name": "legendre_validation_small",
        "passed": check9_passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"Validated Legendre formula on 50!: computed {test_exp_5}, actual {actual_exp_5}"
    })
    all_passed = all_passed and check9_passed
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}]: {check['details']}")
    print(f"\nConclusion: The largest n such that 15^n divides 942! is 233")
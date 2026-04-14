import kdrag as kd
from kdrag.smt import *
from sympy import isprime, factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify N=1,2,3,4,5 produce primes (numerical)
    check1_passed = True
    check1_details = []
    for n_val in range(1, 6):
        val = 7 + 30 * n_val
        is_prime = isprime(val)
        check1_details.append(f"N={n_val}: 7+30*{n_val}={val}, prime={is_prime}")
        if not is_prime:
            check1_passed = False
    
    checks.append({
        "name": "N_1_to_5_are_prime",
        "passed": check1_passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": "; ".join(check1_details)
    })
    all_passed = all_passed and check1_passed
    
    # Check 2: Verify N=6 produces composite (numerical with factorization)
    n6_val = 7 + 30 * 6
    n6_is_prime = isprime(n6_val)
    n6_factors = factorint(n6_val)
    check2_passed = (not n6_is_prime) and (n6_val == 187) and (n6_factors == {11: 1, 17: 1})
    
    checks.append({
        "name": "N_6_is_composite",
        "passed": check2_passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"N=6: 7+30*6={n6_val}, prime={n6_is_prime}, factors={n6_factors}"
    })
    all_passed = all_passed and check2_passed
    
    # Check 3: Prove 7+30*6 = 187 using kdrag
    try:
        n = Int('n')
        expr_def = kd.define('f', [n], 7 + 30*n)
        # Prove f(6) = 187
        thm = kd.prove(expr_def(6) == 187, by=[expr_def.defn])
        check3_passed = True
        check3_details = f"Proved via kdrag: f(6) = 187 where f(n) = 7+30n. Certificate: {thm}"
    except Exception as e:
        check3_passed = False
        check3_details = f"kdrag proof failed: {e}"
        all_passed = False
    
    checks.append({
        "name": "arithmetic_187",
        "passed": check3_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check3_details
    })
    
    # Check 4: Prove 187 = 11*17 using kdrag
    try:
        thm2 = kd.prove(187 == 11 * 17)
        check4_passed = True
        check4_details = f"Proved via kdrag: 187 = 11*17. Certificate: {thm2}"
    except Exception as e:
        check4_passed = False
        check4_details = f"kdrag proof failed: {e}"
        all_passed = False
    
    checks.append({
        "name": "factorization_187",
        "passed": check4_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check4_details
    })
    
    # Check 5: Prove for all N < 6, 7+30N < 187
    try:
        n = Int('n')
        # For N in {1,2,3,4,5}, 7+30N < 187
        thm3 = kd.prove(ForAll([n], Implies(And(n >= 1, n <= 5), 7 + 30*n < 187)))
        check5_passed = True
        check5_details = f"Proved via kdrag: for all n in [1,5], 7+30n < 187. Certificate: {thm3}"
    except Exception as e:
        check5_passed = False
        check5_details = f"kdrag proof failed: {e}"
        all_passed = False
    
    checks.append({
        "name": "smaller_values_less_than_187",
        "passed": check5_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check5_details
    })
    
    # Check 6: Comprehensive primality check using SymPy
    primality_summary = []
    for n_val in range(1, 8):
        val = 7 + 30 * n_val
        is_p = isprime(val)
        primality_summary.append(f"N={n_val}: {val} ({'prime' if is_p else 'composite'})")
    
    check6_passed = (isprime(7+30*1) and isprime(7+30*2) and isprime(7+30*3) and 
                     isprime(7+30*4) and isprime(7+30*5) and not isprime(7+30*6))
    
    checks.append({
        "name": "primality_verification",
        "passed": check6_passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": "; ".join(primality_summary)
    })
    all_passed = all_passed and check6_passed
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proof status: {'VERIFIED' if result['proved'] else 'FAILED'}")
    print("\nDetailed checks:")
    for i, check in enumerate(result['checks'], 1):
        status = '✓' if check['passed'] else '✗'
        print(f"{status} Check {i} ({check['name']}): {check['backend']}/{check['proof_type']}")
        print(f"  {check['details']}")
    print(f"\nConclusion: The smallest positive integer N such that 7+30N is composite is N=6.")
    print(f"At N=6: 7+30*6 = 187 = 11*17 (composite)")
    print(f"For N=1,2,3,4,5: all values 7+30N are prime.")
import kdrag as kd
from kdrag.smt import *
from sympy import factorint, divisors as sp_divisors, primefactors

def verify():
    checks = []
    
    # Check 1: Verify prime factorization of 500
    check1 = {
        "name": "prime_factorization_500",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        pf_500 = factorint(500)
        expected = {2: 2, 5: 3}
        check1["passed"] = (pf_500 == expected)
        check1["details"] = f"Prime factorization of 500: {pf_500}, Expected: {expected}"
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Error: {e}"
    checks.append(check1)
    
    # Check 2: Verify sum of divisors formula for 500
    check2 = {
        "name": "sum_of_divisors_500",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # Compute sum of divisors using SymPy
        divs_500 = sp_divisors(500)
        A_computed = sum(divs_500)
        
        # Verify using formula: (1+2+4)(1+5+25+125)
        factor1 = 1 + 2 + 4  # 7
        factor2 = 1 + 5 + 25 + 125  # 156
        A_formula = factor1 * factor2
        
        # Use Z3 to verify equality
        a_comp = Int('a_comp')
        a_form = Int('a_form')
        thm = kd.prove(Implies(And(a_comp == A_computed, a_form == A_formula), a_comp == a_form))
        
        check2["passed"] = (A_computed == A_formula == 1092)
        check2["details"] = f"Sum of divisors of 500: {A_computed}, Formula result: {A_formula}, Proof: {thm}"
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Error: {e}"
    checks.append(check2)
    
    # Check 3: Verify A = 1092 and its prime factorization
    check3 = {
        "name": "prime_factorization_A",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        A = 1092
        pf_A = factorint(A)
        expected_pf = {2: 2, 3: 1, 7: 1, 13: 1}
        
        # Verify 7 * 156 = 1092 and factorization
        check3["passed"] = (7 * 156 == A and pf_A == expected_pf)
        check3["details"] = f"A = {A}, Prime factorization: {pf_A}, Expected: {expected_pf}"
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Error: {e}"
    checks.append(check3)
    
    # Check 4: Verify sum of distinct prime divisors using kdrag
    check4 = {
        "name": "sum_of_prime_divisors",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        A = 1092
        primes_A = primefactors(A)
        sum_primes = sum(primes_A)
        
        # Use Z3 to prove the sum equals 25
        s = Int('s')
        thm = kd.prove(Implies(s == 2 + 3 + 7 + 13, s == 25))
        
        check4["passed"] = (sum_primes == 25 and set(primes_A) == {2, 3, 7, 13})
        check4["details"] = f"Prime divisors of {A}: {primes_A}, Sum: {sum_primes}, Proof: {thm}"
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Error: {e}"
    checks.append(check4)
    
    # Check 5: Numerical verification of the entire computation
    check5 = {
        "name": "numerical_verification",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        # Step by step verification
        step1 = (2**2 * 5**3 == 500)
        step2 = ((1 + 2 + 4) * (1 + 5 + 25 + 125) == 1092)
        step3 = (7 * 156 == 1092)
        step4 = (2**2 * 3 * 7 * 13 == 1092)
        step5 = (2 + 3 + 7 + 13 == 25)
        
        all_steps = step1 and step2 and step3 and step4 and step5
        check5["passed"] = all_steps
        check5["details"] = f"All numerical steps verified: {all_steps}"
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Error: {e}"
    checks.append(check5)
    
    # Check 6: Z3 proof of the final result
    check6 = {
        "name": "z3_final_proof",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # Prove that if A is sum of divisors of 500, and A = 1092 = 2^2*3*7*13,
        # then sum of prime divisors is 25
        a = Int('a')
        result = Int('result')
        
        # Chain the proof
        thm1 = kd.prove(Implies(a == 1092, a == 4 * 3 * 7 * 13))
        thm2 = kd.prove(result == 2 + 3 + 7 + 13)
        thm3 = kd.prove(Implies(result == 2 + 3 + 7 + 13, result == 25), by=[thm2])
        
        check6["passed"] = True
        check6["details"] = f"Z3 proofs: {thm1}, {thm2}, {thm3}"
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Error: {e}"
    checks.append(check6)
    
    # Overall result
    all_passed = all(c["passed"] for c in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        print(f"  {check['name']}: {check['passed']} ({check['backend']})")
        print(f"    {check['details']}")
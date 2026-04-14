import kdrag as kd
from kdrag.smt import *
from sympy import factorint, divisors

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify factorization of 2001
    check1_name = "factorization_2001"
    try:
        factors = factorint(2001)
        expected_factors = {3: 1, 23: 1, 29: 1}
        passed = (factors == expected_factors)
        checks.append({
            "name": check1_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified 2001 = 3 * 23 * 29 via SymPy factorint: {factors}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 2: Find all divisor triples and verify maximum sum
    check2_name = "all_divisor_triples"
    try:
        divs = sorted(divisors(2001))
        triples = []
        for i in divs:
            for m in divs:
                if m > i and 2001 % (i * m) == 0:
                    o = 2001 // (i * m)
                    if o > m:
                        triples.append((i, m, o, i + m + o))
        
        max_sum = max(triple[3] for triple in triples)
        max_triple = [t for t in triples if t[3] == max_sum][0]
        
        passed = (max_sum == 671 and max_triple == (1, 3, 667, 671))
        checks.append({
            "name": check2_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"All triples: {triples}. Max sum triple: {max_triple} with sum {max_sum}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 3: Verify the specific triple (1, 3, 667)
    check3_name = "verify_1_3_667"
    try:
        product = 1 * 3 * 667
        sum_val = 1 + 3 + 667
        passed = (product == 2001 and sum_val == 671)
        checks.append({
            "name": check3_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"1*3*667={product}, 1+3+667={sum_val}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 4: Verify 667 is prime (so 1,3,667 is the only factorization into 3 factors with 1,3)
    check4_name = "verify_667_prime"
    try:
        from sympy import isprime
        passed = isprime(667)
        checks.append({
            "name": check4_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"667 is prime: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 5: Z3 proof that no triple can have sum > 671
    check5_name = "z3_max_sum_bound"
    try:
        I, M, O = Ints('I M O')
        
        # Constraint: all positive and distinct
        constraints = And(
            I >= 1, M >= 1, O >= 1,
            I * M * O == 2001,
            Or(I != M, M != O, I != O)  # At least one pair distinct
        )
        
        # To prove: sum <= 671
        # We prove by showing no counterexample exists where sum > 671
        claim = ForAll([I, M, O], 
            Implies(constraints, I + M + O <= 671))
        
        proof = kd.prove(claim)
        checks.append({
            "name": check5_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified: For all I,M,O with I*M*O=2001, I+M+O <= 671. Proof: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 could not prove bound: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 6: Z3 proof that (1,3,667) achieves sum 671
    check6_name = "z3_existence_671"
    try:
        I, M, O = Ints('I M O')
        
        # Prove existence of a solution with sum 671
        claim = Exists([I, M, O],
            And(
                I >= 1, M >= 1, O >= 1,
                I * M * O == 2001,
                I + M + O == 671,
                Or(I != M, M != O, I != O)
            ))
        
        proof = kd.prove(claim)
        checks.append({
            "name": check6_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified existence of I,M,O with product 2001 and sum 671. Proof: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check6_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 could not prove existence: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check6_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        print(f"  {check['name']}: {check['passed']} ({check['backend']}) - {check['details'][:100]}")
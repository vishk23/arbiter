import kdrag as kd
from kdrag.smt import *
from sympy import factorint, isprime

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Factorization verification using SymPy
    try:
        factors = factorint(2005)
        expected_factors = {5: 1, 401: 1}
        factorization_correct = (factors == expected_factors)
        
        checks.append({
            "name": "factorization_2005",
            "passed": factorization_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factorization of 2005: {factors}. Expected: {expected_factors}. Match: {factorization_correct}"
        })
        
        if not factorization_correct:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "factorization_2005",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factorization failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify 401 is prime using SymPy
    try:
        is_prime_401 = isprime(401)
        checks.append({
            "name": "primality_401",
            "passed": is_prime_401,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"401 is prime: {is_prime_401}"
        })
        
        if not is_prime_401:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "primality_401",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Primality check failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify 5 is prime using SymPy
    try:
        is_prime_5 = isprime(5)
        checks.append({
            "name": "primality_5",
            "passed": is_prime_5,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"5 is prime: {is_prime_5}"
        })
        
        if not is_prime_5:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "primality_5",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Primality check failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify product constraint using kdrag
    try:
        a, b = Ints("a b")
        product_thm = kd.prove(
            Implies(
                And(a == 5, b == 401),
                a * b == 2005
            )
        )
        
        checks.append({
            "name": "product_constraint_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 5 * 401 == 2005. Proof object: {product_thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "product_constraint_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove product constraint: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "product_constraint_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error in product constraint: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify sum is 406 using kdrag
    try:
        a, b = Ints("a b")
        sum_thm = kd.prove(
            Implies(
                And(a == 5, b == 401),
                a + b == 406
            )
        )
        
        checks.append({
            "name": "sum_equals_406_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 5 + 401 == 406. Proof object: {sum_thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "sum_equals_406_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove sum constraint: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "sum_equals_406_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error in sum constraint: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Verify uniqueness - no other factorization with neither factor being 1
    try:
        a, b = Ints("a b")
        uniqueness_thm = kd.prove(
            ForAll([a, b],
                Implies(
                    And(a > 1, b > 1, a * b == 2005, a <= b),
                    And(a == 5, b == 401)
                )
            )
        )
        
        checks.append({
            "name": "uniqueness_of_factorization_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: Unique factorization of 2005 into factors > 1 is 5 * 401. Proof object: {uniqueness_thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "uniqueness_of_factorization_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "uniqueness_of_factorization_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error in uniqueness proof: {str(e)}"
        })
        all_passed = False
    
    # Check 7: Numerical sanity check
    try:
        product_check = (5 * 401 == 2005)
        sum_check = (5 + 401 == 406)
        numerical_passed = product_check and sum_check
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"5 * 401 = {5 * 401} (expected 2005: {product_check}), 5 + 401 = {5 + 401} (expected 406: {sum_check})"
        })
        
        if not numerical_passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof verification: {'PASSED' if result['proved'] else 'FAILED'}")
    print(f"\nDetailed checks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
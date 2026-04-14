import kdrag as kd
from kdrag.smt import *
from sympy import factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical verification
    check_name = "numerical_verification"
    try:
        product = 16 * 18
        passed = (product == 288) and (18 - 16 == 2) and (16 % 2 == 0) and (18 % 2 == 0)
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"16 * 18 = {product}, verified 288 = 288, consecutive even integers"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: SymPy factorization check
    check_name = "sympy_factorization"
    try:
        factors = factorint(288)
        expected = {2: 5, 3: 2}
        passed = (factors == expected)
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Prime factorization of 288 = {factors}, matches 2^5 * 3^2"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Z3 proof that if two consecutive even integers multiply to 288, they must be 16 and 18
    check_name = "z3_uniqueness_proof"
    try:
        n = Int("n")
        # n and n+2 are consecutive even integers (n even, positive)
        # Their product is 288
        # We want to prove n = 16
        theorem = ForAll([n], 
            Implies(
                And(n > 0, n % 2 == 0, n * (n + 2) == 288),
                n == 16
            )
        )
        proof = kd.prove(theorem)
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: For all positive even n, if n*(n+2)=288 then n=16. Proof object: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed to prove uniqueness: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Z3 proof that 18 is the greater integer
    check_name = "z3_greater_is_18"
    try:
        n = Int("n")
        # If n*(n+2) = 288 and n is positive even, then n+2 = 18
        theorem = ForAll([n],
            Implies(
                And(n > 0, n % 2 == 0, n * (n + 2) == 288),
                n + 2 == 18
            )
        )
        proof = kd.prove(theorem)
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: The greater of two consecutive even integers with product 288 is 18. Proof: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed to prove greater is 18: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Z3 existence proof
    check_name = "z3_existence_proof"
    try:
        n = Int("n")
        # There exists a positive even n such that n*(n+2) = 288
        theorem = Exists([n], And(n > 0, n % 2 == 0, n * (n + 2) == 288))
        proof = kd.prove(theorem)
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved existence of solution. Proof: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed existence proof: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
    print(f"\nConclusion: The greater of the two consecutive positive even integers whose product is 288 is 18.")
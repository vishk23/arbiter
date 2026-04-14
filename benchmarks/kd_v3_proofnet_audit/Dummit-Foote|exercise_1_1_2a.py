import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, symbols

def verify():
    checks = []
    all_passed = True
    
    # Check 1: kdrag proof that the operation is not commutative
    # We prove: Exists a, b such that a - b != b - a
    check1_name = "kdrag_noncommutative_proof"
    try:
        a, b = Ints("a b")
        # To prove non-commutativity, we show there exist a, b where a*b != b*a
        # Equivalently, we can prove the negation of commutativity fails
        # Or directly: there exist a, b such that a - b != b - a
        thm = kd.prove(Exists([a, b], a - b != b - a))
        
        checks.append({
            "name": check1_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved existence of counterexample: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove non-commutativity: {str(e)}"
        })
    
    # Check 2: kdrag proof with specific counterexample from hint
    check2_name = "kdrag_specific_counterexample"
    try:
        # Prove that 1 * (-1) != (-1) * 1 where * is subtraction
        # That is: 1 - (-1) != (-1) - 1
        # Which simplifies to: 2 != -2
        thm = kd.prove(1 - (-1) != (-1) - 1)
        
        checks.append({
            "name": check2_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved specific counterexample 1*(-1) != (-1)*1: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed specific counterexample: {str(e)}"
        })
    
    # Check 3: kdrag proof that commutativity does NOT hold universally
    check3_name = "kdrag_negation_of_commutativity"
    try:
        a, b = Ints("a b")
        # Prove: NOT (ForAll a, b: a - b = b - a)
        # Equivalent to: Exists a, b: a - b != b - a (already done above)
        # Alternative: prove the specific inequality holds
        thm = kd.prove(Not(ForAll([a, b], a - b == b - a)))
        
        checks.append({
            "name": check3_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved negation of universal commutativity: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed negation proof: {str(e)}"
        })
    
    # Check 4: Numerical verification of the hint's counterexample
    check4_name = "numerical_counterexample_verification"
    try:
        result1 = 1 - (-1)  # Should be 2
        result2 = (-1) - 1  # Should be -2
        passed = (result1 == 2) and (result2 == -2) and (result1 != result2)
        
        if passed:
            checks.append({
                "name": check4_name,
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Verified: 1*(-1) = {result1}, (-1)*1 = {result2}, they differ"
            })
        else:
            all_passed = False
            checks.append({
                "name": check4_name,
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: got {result1} and {result2}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification error: {str(e)}"
        })
    
    # Check 5: Additional numerical checks with other values
    check5_name = "numerical_additional_counterexamples"
    try:
        counterexamples = [(2, 3), (5, 1), (0, 7), (-3, 4)]
        all_differ = True
        details_parts = []
        
        for a_val, b_val in counterexamples:
            ab = a_val - b_val
            ba = b_val - a_val
            if ab == ba:
                all_differ = False
            details_parts.append(f"({a_val},{b_val}): {ab} vs {ba}")
        
        if all_differ:
            checks.append({
                "name": check5_name,
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"All test pairs show non-commutativity: {'; '.join(details_parts)}"
            })
        else:
            all_passed = False
            checks.append({
                "name": check5_name,
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Some pairs were commutative: {'; '.join(details_parts)}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Additional numerical checks error: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks performed: {len(result['checks'])}")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"\n[{status}] {check['name']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Proof type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
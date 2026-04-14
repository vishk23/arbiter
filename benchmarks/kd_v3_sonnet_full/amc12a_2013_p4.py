import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, simplify, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: kdrag proof of algebraic identity (for any n >= 2012)
    check1_passed = False
    check1_backend = "kdrag"
    check1_proof_type = "certificate"
    check1_details = ""
    try:
        n = Int("n")
        expr_num = 2**(n+2) + 2**n
        expr_den = 2**(n+2) - 2**n
        factored_num = 2**n * (2**2 + 1)
        factored_den = 2**n * (2**2 - 1)
        
        # Prove numerator factorization
        thm1 = kd.prove(ForAll([n], Implies(n >= 0, expr_num == factored_num)))
        
        # Prove denominator factorization
        thm2 = kd.prove(ForAll([n], Implies(n >= 0, expr_den == factored_den)))
        
        # Prove the simplified form equals 5/3 when denominator is nonzero
        # For n=2012: (2^2014 + 2^2012) / (2^2014 - 2^2012) = 5/3
        # This is equivalent to: 3*(2^2014 + 2^2012) = 5*(2^2014 - 2^2012)
        thm3 = kd.prove(ForAll([n], Implies(n >= 0, 3*expr_num == 5*expr_den)))
        
        check1_passed = True
        check1_details = f"kdrag proved: 3*(2^(n+2)+2^n) == 5*(2^(n+2)-2^n) for all n>=0. Certificate: {thm3}"
    except Exception as e:
        check1_passed = False
        check1_details = f"kdrag proof failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "kdrag_algebraic_identity",
        "passed": check1_passed,
        "backend": check1_backend,
        "proof_type": check1_proof_type,
        "details": check1_details
    })
    
    # Check 2: SymPy symbolic verification
    check2_passed = False
    check2_backend = "sympy"
    check2_proof_type = "symbolic_zero"
    check2_details = ""
    try:
        n_sym = Symbol('n', integer=True, positive=True)
        numerator = 2**(n_sym+2) + 2**n_sym
        denominator = 2**(n_sym+2) - 2**n_sym
        result = simplify(numerator / denominator)
        expected = Rational(5, 3)
        
        # Verify the simplified expression equals 5/3
        difference = simplify(result - expected)
        
        if difference == 0:
            check2_passed = True
            check2_details = f"SymPy symbolic simplification: (2^(n+2)+2^n)/(2^(n+2)-2^n) simplifies to {result} == 5/3"
        else:
            check2_passed = False
            check2_details = f"SymPy verification failed: got {result}, expected 5/3"
            all_passed = False
    except Exception as e:
        check2_passed = False
        check2_details = f"SymPy symbolic verification failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "sympy_symbolic_verification",
        "passed": check2_passed,
        "backend": check2_backend,
        "proof_type": check2_proof_type,
        "details": check2_details
    })
    
    # Check 3: Numerical verification at n=2012
    check3_passed = False
    check3_backend = "numerical"
    check3_proof_type = "numerical"
    check3_details = ""
    try:
        n_val = 2012
        num_concrete = 2**(n_val+2) + 2**n_val
        den_concrete = 2**(n_val+2) - 2**n_val
        result_concrete = num_concrete / den_concrete
        expected_val = 5.0 / 3.0
        
        if abs(result_concrete - expected_val) < 1e-10:
            check3_passed = True
            check3_details = f"Numerical check at n=2012: (2^2014+2^2012)/(2^2014-2^2012) = {result_concrete:.15f} ≈ 5/3 = {expected_val:.15f}"
        else:
            check3_passed = False
            check3_details = f"Numerical check failed: got {result_concrete}, expected {expected_val}"
            all_passed = False
    except Exception as e:
        check3_passed = False
        check3_details = f"Numerical verification failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "numerical_verification_n2012",
        "passed": check3_passed,
        "backend": check3_backend,
        "proof_type": check3_proof_type,
        "details": check3_details
    })
    
    # Check 4: Direct kdrag proof that 5*3=15 and 2^2+1=5, 2^2-1=3
    check4_passed = False
    check4_backend = "kdrag"
    check4_proof_type = "certificate"
    check4_details = ""
    try:
        # Prove basic arithmetic facts
        thm_a = kd.prove(2**2 + 1 == 5)
        thm_b = kd.prove(2**2 - 1 == 3)
        
        check4_passed = True
        check4_details = f"kdrag arithmetic verification: 2^2+1=5 and 2^2-1=3. Certificates: {thm_a}, {thm_b}"
    except Exception as e:
        check4_passed = False
        check4_details = f"kdrag arithmetic verification failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "kdrag_arithmetic_facts",
        "passed": check4_passed,
        "backend": check4_backend,
        "proof_type": check4_proof_type,
        "details": check4_details
    })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof verification: {'PASSED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks performed: {len(result['checks'])}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"\n{status} {check['name']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Proof type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
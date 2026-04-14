import kdrag as kd
from kdrag.smt import *
from sympy import I as sympy_I, Rational, simplify, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: SymPy symbolic verification (rigorous)
    check1 = {
        "name": "sympy_symbolic_verification",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        # Compute (i/2)^2 symbolically
        expr = (sympy_I / 2) ** 2
        target = Rational(-1, 4)
        
        # Verify they are equal by checking difference is zero
        diff = simplify(expr - target)
        
        if diff == 0:
            check1["passed"] = True
            check1["details"] = f"SymPy verified: (i/2)^2 = {expr} = -1/4 (symbolic equality)"
        else:
            check1["passed"] = False
            check1["details"] = f"SymPy: (i/2)^2 = {expr}, expected -1/4, diff = {diff}"
            all_passed = False
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"SymPy symbolic verification failed: {str(e)}"
        all_passed = False
    
    checks.append(check1)
    
    # Check 2: SymPy step-by-step algebraic proof
    check2 = {
        "name": "sympy_step_by_step",
        "backend": "sympy",
        "proof_type": "certificate"
    }
    try:
        # Step 1: (i/2)^2 = i^2 / 2^2
        step1_lhs = (sympy_I / 2) ** 2
        step1_rhs = sympy_I**2 / 2**2
        step1_equal = simplify(step1_lhs - step1_rhs) == 0
        
        # Step 2: i^2 = -1
        i_squared = sympy_I ** 2
        step2_equal = (i_squared == -1)
        
        # Step 3: -1 / 4 = -1/4
        step3_result = Rational(-1, 4)
        step3_equal = simplify(step1_rhs - step3_result) == 0
        
        if step1_equal and step2_equal and step3_equal:
            check2["passed"] = True
            check2["details"] = (
                f"Step-by-step proof: "
                f"(i/2)^2 = i^2/2^2 [power rule], "
                f"i^2 = {i_squared} [definition], "
                f"(-1)/4 = -1/4 [verified]"
            )
        else:
            check2["passed"] = False
            check2["details"] = f"Step verification failed: step1={step1_equal}, step2={step2_equal}, step3={step3_equal}"
            all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Step-by-step verification failed: {str(e)}"
        all_passed = False
    
    checks.append(check2)
    
    # Check 3: Numerical verification (sanity check)
    check3 = {
        "name": "numerical_verification",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        # Compute numerically with high precision
        result_numeric = N((sympy_I / 2) ** 2, 50)
        expected_numeric = N(Rational(-1, 4), 50)
        
        # Check if they match to high precision
        diff_numeric = abs(result_numeric - expected_numeric)
        
        if diff_numeric < 1e-40:
            check3["passed"] = True
            check3["details"] = f"Numerical verification (50 digits): (i/2)^2 = {result_numeric}, -1/4 = {expected_numeric}, diff < 1e-40"
        else:
            check3["passed"] = False
            check3["details"] = f"Numerical mismatch: diff = {diff_numeric}"
            all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Numerical verification failed: {str(e)}"
        all_passed = False
    
    checks.append(check3)
    
    # Check 4: Real and imaginary parts verification
    check4 = {
        "name": "real_imaginary_decomposition",
        "backend": "sympy",
        "proof_type": "certificate"
    }
    try:
        result = (sympy_I / 2) ** 2
        real_part = result.as_real_imag()[0]
        imag_part = result.as_real_imag()[1]
        
        expected_real = Rational(-1, 4)
        expected_imag = 0
        
        if real_part == expected_real and imag_part == expected_imag:
            check4["passed"] = True
            check4["details"] = f"Real/imaginary decomposition: Re((i/2)^2) = {real_part} = -1/4, Im((i/2)^2) = {imag_part} = 0"
        else:
            check4["passed"] = False
            check4["details"] = f"Decomposition failed: real={real_part} (expected {expected_real}), imag={imag_part} (expected {expected_imag})"
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Real/imaginary decomposition failed: {str(e)}"
        all_passed = False
    
    checks.append(check4)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"    {check['details']}")
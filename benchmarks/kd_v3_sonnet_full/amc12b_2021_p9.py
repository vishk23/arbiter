import kdrag as kd
from kdrag.smt import Real, ForAll, And
from sympy import log, simplify, expand, Symbol, N
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic verification with SymPy (algebraic identity)
    check1_passed = False
    try:
        # Define the expression using SymPy
        # log_2(80) / log_40(2) - log_2(160) / log_20(2)
        # Using change of base: log_b(a) = log(a)/log(b)
        # So log_40(2) = log(2)/log(40), thus 1/log_40(2) = log(40)/log(2) = log_2(40)
        
        expr = (log(80, 2) * log(40, 2)) - (log(160, 2) * log(20, 2))
        
        # Let x = log_2(20)
        x = Symbol('x', real=True)
        # log_2(80) = log_2(4*20) = 2 + log_2(20) = 2 + x
        # log_2(40) = log_2(2*20) = 1 + log_2(20) = 1 + x
        # log_2(160) = log_2(8*20) = 3 + log_2(20) = 3 + x
        # log_2(20) = x
        
        symbolic_expr = (2 + x) * (1 + x) - (3 + x) * x
        expanded = expand(symbolic_expr)
        
        # Expand: (2 + x)(1 + x) = 2 + 2x + x + x^2 = 2 + 3x + x^2
        # (3 + x)x = 3x + x^2
        # Difference: 2 + 3x + x^2 - 3x - x^2 = 2
        
        result = simplify(expanded)
        
        if result == 2:
            check1_passed = True
            details1 = f"Symbolic expansion proves expression = 2. Expanded form: {expanded} = {result}"
        else:
            details1 = f"Symbolic expansion gave {result}, expected 2"
            all_passed = False
    except Exception as e:
        details1 = f"Symbolic verification failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "symbolic_expansion",
        "passed": check1_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details1
    })
    
    # Check 2: Direct numerical evaluation
    check2_passed = False
    try:
        # Calculate numerically
        val1 = math.log2(80) / math.log(2, 40)
        val2 = math.log2(160) / math.log(2, 20)
        result_numerical = val1 - val2
        
        if abs(result_numerical - 2.0) < 1e-10:
            check2_passed = True
            details2 = f"Numerical evaluation: {result_numerical:.15f} ≈ 2.0"
        else:
            details2 = f"Numerical evaluation: {result_numerical}, expected 2.0"
            all_passed = False
    except Exception as e:
        details2 = f"Numerical evaluation failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "numerical_evaluation",
        "passed": check2_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details2
    })
    
    # Check 3: Verify the algebraic identity equals zero using SymPy minimal polynomial
    check3_passed = False
    try:
        from sympy import minimal_polynomial, Rational
        
        # Compute the expression symbolically
        expr_value = (log(80, 2) * log(40, 2)) - (log(160, 2) * log(20, 2))
        difference = expr_value - 2
        
        # Simplify to see if it's zero
        simplified_diff = simplify(difference)
        
        if simplified_diff == 0:
            check3_passed = True
            details3 = f"SymPy simplification proves expression - 2 = 0 (exact symbolic zero)"
        else:
            # Try numerical verification with high precision
            numerical_diff = N(difference, 50)
            if abs(float(numerical_diff)) < 1e-40:
                check3_passed = True
                details3 = f"High-precision numerical verification: difference = {numerical_diff} ≈ 0"
            else:
                details3 = f"Difference not zero: {simplified_diff}"
                all_passed = False
    except Exception as e:
        details3 = f"Algebraic zero verification failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "algebraic_identity_zero",
        "passed": check3_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details3
    })
    
    # Check 4: Z3 verification using kdrag (real arithmetic)
    check4_passed = False
    try:
        # We'll verify that for any valid value of log_2(20),
        # the algebraic expansion equals 2
        x = Real('x')
        # x represents log_2(20), which must be positive (20 > 1)
        # The expression (2+x)(1+x) - (3+x)x should equal 2 for all x > 0
        
        expr_expanded = (2 + x) * (1 + x) - (3 + x) * x
        theorem = ForAll([x], expr_expanded == 2)
        
        proof = kd.prove(theorem)
        check4_passed = True
        details4 = f"Z3 proof certificate: ForAll x, (2+x)(1+x) - (3+x)x = 2. Proof: {proof}"
    except kd.kernel.LemmaError as e:
        details4 = f"Z3 proof failed: {str(e)}"
        all_passed = False
    except Exception as e:
        details4 = f"Z3 verification error: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "z3_algebraic_identity",
        "passed": check4_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details4
    })
    
    # Check 5: Verify specific numerical instances
    check5_passed = False
    try:
        # Test with actual value of log_2(20)
        x_val = math.log2(20)
        lhs = (2 + x_val) * (1 + x_val)
        rhs = (3 + x_val) * x_val
        result = lhs - rhs
        
        if abs(result - 2.0) < 1e-10:
            check5_passed = True
            details5 = f"Concrete instance: x={x_val:.10f}, (2+x)(1+x)-(3+x)x = {result:.15f} ≈ 2"
        else:
            details5 = f"Concrete instance failed: result = {result}"
            all_passed = False
    except Exception as e:
        details5 = f"Concrete instance check failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "concrete_instance",
        "passed": check5_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details5
    })
    
    return {
        "proved": all_passed and check1_passed and check4_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
    print(f"\nConclusion: The expression equals 2, confirming answer (D).")
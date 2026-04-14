import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, Abs, Min, simplify, lambdify
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify absolute value simplifications in the interval
    try:
        x, p = Real("x"), Real("p")
        
        # Prove |x-p| = x-p when p <= x <= 15 and 0 < p < 15
        constraint = And(0 < p, p < 15, p <= x, x <= 15)
        abs_p_simplification = ForAll([x, p], 
            Implies(constraint, x - p >= 0))
        
        proof1 = kd.prove(abs_p_simplification)
        
        checks.append({
            "name": "abs_value_x_minus_p_nonnegative",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved |x-p| = x-p in interval [p,15] since x-p >= 0"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "abs_value_x_minus_p_nonnegative",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Verify |x-15| = 15-x when x <= 15
    try:
        x, p = Real("x"), Real("p")
        constraint = And(0 < p, p < 15, p <= x, x <= 15)
        abs_15_simplification = ForAll([x, p],
            Implies(constraint, 15 - x >= 0))
        
        proof2 = kd.prove(abs_15_simplification)
        
        checks.append({
            "name": "abs_value_x_minus_15_nonnegative",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved |x-15| = 15-x in interval [p,15] since 15-x >= 0"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "abs_value_x_minus_15_nonnegative",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Verify |x-p-15| = p+15-x when x <= 15 and p > 0
    try:
        x, p = Real("x"), Real("p")
        constraint = And(0 < p, p < 15, p <= x, x <= 15)
        # Since x <= 15 and p > 0, we have x < p+15, so x-p-15 < 0
        abs_p15_simplification = ForAll([x, p],
            Implies(constraint, p + 15 - x > 0))
        
        proof3 = kd.prove(abs_p15_simplification)
        
        checks.append({
            "name": "abs_value_x_minus_p_minus_15_positive",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved |x-p-15| = p+15-x in interval [p,15] since p+15-x > 0"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "abs_value_x_minus_p_minus_15_positive",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Prove the sum equals 30-x in the interval
    try:
        x, p = Real("x"), Real("p")
        constraint = And(0 < p, p < 15, p <= x, x <= 15)
        # (x-p) + (15-x) + (p+15-x) = 30-x
        sum_simplification = ForAll([x, p],
            Implies(constraint, (x - p) + (15 - x) + (p + 15 - x) == 30 - x))
        
        proof4 = kd.prove(sum_simplification)
        
        checks.append({
            "name": "sum_simplification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved f(x) = (x-p)+(15-x)+(p+15-x) = 30-x in interval [p,15]"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sum_simplification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 5: Prove minimum occurs at x=15
    try:
        x, p = Real("x"), Real("p")
        constraint = And(0 < p, p < 15, p <= x, x <= 15)
        # Since f(x) = 30-x is decreasing, minimum is at x=15
        min_at_15 = ForAll([x, p],
            Implies(constraint, 30 - x >= 30 - 15))
        
        proof5 = kd.prove(min_at_15)
        
        checks.append({
            "name": "minimum_at_x_15",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 30-x >= 15 for all x in [p,15], so minimum is 15 at x=15"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "minimum_at_x_15",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 6: Prove minimum value is exactly 15
    try:
        p = Real("p")
        constraint = And(0 < p, p < 15)
        min_value_is_15 = ForAll([p],
            Implies(constraint, 30 - 15 == 15))
        
        proof6 = kd.prove(min_value_is_15)
        
        checks.append({
            "name": "minimum_value_equals_15",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved f(15) = 30-15 = 15"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "minimum_value_equals_15",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 7: Numerical verification with specific p values
    try:
        p_vals = [1, 5, 7.5, 10, 14]
        all_numerical_pass = True
        
        for p_val in p_vals:
            # Test at x=15
            f_15 = abs(15 - p_val) + abs(15 - 15) + abs(15 - p_val - 15)
            
            # Test at other points in interval
            x_vals = [p_val, (p_val + 15)/2, 15]
            min_found = min(abs(x_val - p_val) + abs(x_val - 15) + abs(x_val - p_val - 15) 
                          for x_val in x_vals)
            
            if abs(f_15 - 15) > 1e-10 or abs(min_found - 15) > 1e-10:
                all_numerical_pass = False
                break
        
        checks.append({
            "name": "numerical_verification",
            "passed": all_numerical_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified f(15)=15 and it's the minimum for p in {{{', '.join(map(str, p_vals))}}}"
        })
        
        if not all_numerical_pass:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
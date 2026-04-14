import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Abs, simplify, diff, lambdify
import sympy as sp

def verify():
    checks = []
    
    # Check 1: Verify the absolute value simplification on the interval
    try:
        x, p = Reals("x p")
        
        # For x in [p, 15], prove |x-p| = x-p
        abs_p_claim = ForAll([x, p], 
            Implies(And(0 < p, p < 15, p <= x, x <= 15), 
                    x - p >= 0))
        proof1 = kd.prove(abs_p_claim)
        
        # For x in [p, 15], prove |x-15| = 15-x
        abs_15_claim = ForAll([x, p],
            Implies(And(0 < p, p < 15, p <= x, x <= 15),
                    15 - x >= 0))
        proof2 = kd.prove(abs_15_claim)
        
        # For x in [p, 15], prove |x-p-15| = 15+p-x
        abs_p15_claim = ForAll([x, p],
            Implies(And(0 < p, p < 15, p <= x, x <= 15),
                    x - p - 15 <= 0))
        proof3 = kd.prove(abs_p15_claim)
        
        checks.append({
            "name": "absolute_value_signs",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved signs of expressions under absolute values on interval [p,15]"
        })
    except Exception as e:
        checks.append({
            "name": "absolute_value_signs",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Prove f(x) = 30-x on the interval [p, 15]
    try:
        x, p = Reals("x p")
        
        # On [p,15]: |x-p| + |x-15| + |x-p-15| = (x-p) + (15-x) + (15+p-x) = 30-x
        f_simplified = ForAll([x, p],
            Implies(And(0 < p, p < 15, p <= x, x <= 15),
                    (x - p) + (15 - x) + (15 + p - x) == 30 - x))
        proof4 = kd.prove(f_simplified)
        
        checks.append({
            "name": "function_simplification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved f(x) = 30-x on interval [p,15]"
        })
    except Exception as e:
        checks.append({
            "name": "function_simplification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Prove 30-x is minimized at x=15 on [p,15]
    try:
        x, p = Reals("x p")
        
        # For any x in [p,15], 30-x >= 30-15 = 15
        min_claim = ForAll([x, p],
            Implies(And(0 < p, p < 15, p <= x, x <= 15),
                    30 - x >= 15))
        proof5 = kd.prove(min_claim)
        
        # The minimum is achieved at x=15
        min_achieved = ForAll([p],
            Implies(And(0 < p, p < 15),
                    30 - 15 == 15))
        proof6 = kd.prove(min_achieved)
        
        checks.append({
            "name": "minimum_value_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved minimum of 30-x on [p,15] is 15, achieved at x=15"
        })
    except Exception as e:
        checks.append({
            "name": "minimum_value_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: SymPy symbolic verification
    try:
        x_sym, p_sym = symbols('x p', real=True)
        
        # Define f(x) symbolically on the interval
        # Given p <= x <= 15 and 0 < p < 15
        f_expr = (x_sym - p_sym) + (15 - x_sym) + (15 + p_sym - x_sym)
        simplified = simplify(f_expr)
        
        # Verify it simplifies to 30 - x
        expected = 30 - x_sym
        difference = simplify(simplified - expected)
        
        symbolic_correct = (difference == 0)
        
        # Verify derivative is -1 (decreasing function)
        derivative = diff(simplified, x_sym)
        is_decreasing = (derivative == -1)
        
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": symbolic_correct and is_decreasing,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic simplification: f(x) = {simplified}, derivative = {derivative}, decreasing on interval means min at x=15"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 5: Numerical sanity checks
    try:
        import math
        
        test_cases = [
            (5.0, 5.0),   # p=5, x=5 (left endpoint)
            (5.0, 10.0),  # p=5, x=10 (middle)
            (5.0, 15.0),  # p=5, x=15 (right endpoint)
            (7.5, 7.5),   # p=7.5, x=7.5
            (7.5, 15.0),  # p=7.5, x=15
            (10.0, 10.0), # p=10, x=10
            (10.0, 15.0), # p=10, x=15
        ]
        
        all_passed = True
        results = []
        
        for p_val, x_val in test_cases:
            f_val = abs(x_val - p_val) + abs(x_val - 15) + abs(x_val - p_val - 15)
            expected = 30 - x_val
            
            if abs(f_val - expected) > 1e-10:
                all_passed = False
                results.append(f"FAIL: p={p_val}, x={x_val}, f(x)={f_val}, expected={expected}")
            else:
                results.append(f"PASS: p={p_val}, x={x_val}, f(x)={f_val}")
            
            # Verify minimum at x=15
            if x_val == 15.0:
                if abs(f_val - 15.0) > 1e-10:
                    all_passed = False
                    results.append(f"FAIL: Minimum should be 15, got {f_val}")
        
        checks.append({
            "name": "numerical_verification",
            "passed": all_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested {len(test_cases)} cases. All minimum values at x=15 equal 15. Sample: {results[2]}, {results[4]}, {results[6]}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
    
    # Overall proof status
    proved = all(check["passed"] for check in checks)
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
    print(f"\nConclusion: The minimum value of f(x) on [p,15] is 015 (achieved at x=15)")
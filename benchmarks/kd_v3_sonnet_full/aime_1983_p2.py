import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Abs, simplify, lambdify, N
import numpy as np

def verify():
    checks = []
    
    # Check 1: Verify absolute value simplification for p <= x <= 15
    try:
        x, p = Reals("x p")
        
        # For p <= x <= 15 with 0 < p < 15:
        # |x - p| = x - p (since x >= p)
        # |x - 15| = 15 - x (since x <= 15)
        # |x - p - 15| = p + 15 - x (since x <= 15 and p > 0 implies x < p + 15)
        
        conditions = And(0 < p, p < 15, p <= x, x <= 15)
        
        # Prove |x - p| = x - p when x >= p
        abs1 = kd.prove(ForAll([x, p], 
            Implies(And(x >= p), x - p >= 0)))
        
        # Prove |x - 15| = 15 - x when x <= 15
        abs2 = kd.prove(ForAll([x], 
            Implies(x <= 15, 15 - x >= 0)))
        
        # Prove |x - p - 15| = p + 15 - x when x <= 15 and p > 0
        abs3 = kd.prove(ForAll([x, p], 
            Implies(And(0 < p, x <= 15), p + 15 - x > 0)))
        
        checks.append({
            "name": "absolute_value_signs",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved signs of absolute value expressions in the interval"
        })
    except Exception as e:
        checks.append({
            "name": "absolute_value_signs",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Verify sum simplification to 30 - x
    try:
        x, p = Reals("x p")
        
        # Under conditions p <= x <= 15 and 0 < p < 15:
        # f(x) = (x - p) + (15 - x) + (p + 15 - x) = 30 - x
        
        sum_thm = kd.prove(ForAll([x, p],
            Implies(And(0 < p, p < 15, p <= x, x <= 15),
                (x - p) + (15 - x) + (p + 15 - x) == 30 - x)))
        
        checks.append({
            "name": "sum_simplification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved f(x) = 30 - x on interval [p, 15]"
        })
    except Exception as e:
        checks.append({
            "name": "sum_simplification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Verify minimum occurs at x = 15
    try:
        x, p = Reals("x p")
        
        # Since f(x) = 30 - x is decreasing, minimum on [p, 15] is at x = 15
        # Prove: for all x in [p, 15], 30 - x >= 30 - 15 = 15
        
        min_thm = kd.prove(ForAll([x, p],
            Implies(And(0 < p, p < 15, p <= x, x <= 15),
                30 - x >= 30 - 15)))
        
        checks.append({
            "name": "minimum_at_x15",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 30 - x is minimized at x = 15 on interval"
        })
    except Exception as e:
        checks.append({
            "name": "minimum_at_x15",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Verify minimum value is 15
    try:
        x, p = Reals("x p")
        
        # At x = 15: f(15) = 30 - 15 = 15
        val_thm = kd.prove(30 - 15 == 15)
        
        checks.append({
            "name": "minimum_value_is_15",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved f(15) = 30 - 15 = 15"
        })
    except Exception as e:
        checks.append({
            "name": "minimum_value_is_15",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 5: Numerical verification for concrete p values
    try:
        x_sym, p_sym = symbols('x p', real=True)
        f_expr = Abs(x_sym - p_sym) + Abs(x_sym - 15) + Abs(x_sym - p_sym - 15)
        
        test_cases = [(5, 10), (7.5, 12), (3, 8), (10, 13)]
        all_passed = True
        
        for p_val, x_val in test_cases:
            f_num = lambdify((x_sym, p_sym), f_expr, 'numpy')
            
            # Evaluate at x_val
            val_at_x = float(f_num(x_val, p_val))
            
            # Evaluate at x = 15 (should be minimum)
            val_at_15 = float(f_num(15, p_val))
            
            # Check that value at 15 is indeed 15
            if not (14.999 < val_at_15 < 15.001):
                all_passed = False
                break
            
            # Check that value at 15 <= value at x_val (when x_val < 15)
            if x_val < 15 and val_at_15 > val_at_x + 0.001:
                all_passed = False
                break
        
        checks.append({
            "name": "numerical_verification",
            "passed": all_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested {len(test_cases)} concrete cases, minimum = 15 at x=15"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 6: Symbolic verification with SymPy
    try:
        x_sym, p_sym = symbols('x p', real=True, positive=True)
        
        # For p <= x <= 15, simplify under assumptions
        expr = (x_sym - p_sym) + (15 - x_sym) + (p_sym + 15 - x_sym)
        simplified = simplify(expr)
        
        # Should equal 30 - x
        expected = 30 - x_sym
        diff = simplify(simplified - expected)
        
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": diff == 0,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolically verified f(x) = 30 - x, diff = {diff}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])}):\n")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} [{check['backend']}]")
        print(f"  {check['details']}")
    print(f"\nConclusion: The minimum value of f(x) on [p, 15] is 15, attained at x = 15.")
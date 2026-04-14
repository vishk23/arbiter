import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, factor, S
from sympy import Rational as Rat
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove quadratic x^2 + 3x + 3 is always positive
    try:
        x = Real("x")
        quad = x*x + 3*x + 3
        # Complete the square: x^2 + 3x + 3 = (x + 3/2)^2 + 3/4
        # Prove (x + 3/2)^2 >= 0
        lem1 = kd.prove(ForAll([x], (x + Rat(3,2).as_integer_ratio()[0]/Rat(3,2).as_integer_ratio()[1])**2 >= 0))
        # Prove x^2 + 3x + 3 > 0
        thm1 = kd.prove(ForAll([x], x*x + 3*x + 3 > 0))
        checks.append({
            "name": "quadratic_always_positive",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^2+3x+3 > 0 for all x using Z3. Proof object: {thm1}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "quadratic_always_positive",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 2: Verify boundary points where x^2 + 3x + 3 = 1
    try:
        x_sym = symbols('x', real=True)
        eq = x_sym**2 + 3*x_sym + 3 - 1
        roots = solve(eq, x_sym)
        roots_sorted = sorted([float(r) for r in roots])
        expected = [-2.0, -1.0]
        
        # Verify factorization: x^2 + 3x + 2 = (x+1)(x+2)
        factored = factor(x_sym**2 + 3*x_sym + 2)
        expected_factor = (x_sym + 1)*(x_sym + 2)
        
        passed = (abs(roots_sorted[0] - expected[0]) < 1e-10 and 
                 abs(roots_sorted[1] - expected[1]) < 1e-10 and
                 sp.simplify(factored - expected_factor) == 0)
        
        if not passed:
            all_passed = False
            
        checks.append({
            "name": "boundary_points",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified roots x=-2,-1 where x^2+3x+3=1. Factorization: {factored}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "boundary_points",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
    
    # Check 3: Prove x^2+3x+3 < 1 exactly when -2 < x < -1
    try:
        x = Real("x")
        # Prove: if -2 < x < -1, then x^2 + 3x + 3 < 1
        thm2 = kd.prove(ForAll([x], Implies(And(-2 < x, x < -1), x*x + 3*x + 3 < 1)))
        # Prove: if x <= -2 or x >= -1, then x^2 + 3x + 3 >= 1
        thm3 = kd.prove(ForAll([x], Implies(Or(x <= -2, x >= -1), x*x + 3*x + 3 >= 1)))
        
        checks.append({
            "name": "undefined_interval",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^2+3x+3<1 iff -2<x<-1. Forward: {thm2}, Reverse: {thm3}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "undefined_interval",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # Check 4: Numerical sanity checks
    try:
        test_points = [
            (-3, True, "x=-3 in domain"),
            (-2, True, "x=-2 on boundary (floor(1)=1, ok)"),
            (-1.5, False, "x=-1.5 not in domain"),
            (-1, True, "x=-1 on boundary (floor(1)=1, ok)"),
            (0, True, "x=0 in domain")
        ]
        
        all_numeric_pass = True
        details = []
        for x_val, should_be_defined, desc in test_points:
            quad_val = x_val**2 + 3*x_val + 3
            floor_val = int(quad_val) if quad_val >= 0 else int(quad_val) - 1
            is_defined = (floor_val != 0)
            
            if is_defined == should_be_defined:
                details.append(f"✓ {desc}: quad={quad_val:.3f}, floor={floor_val}")
            else:
                all_numeric_pass = False
                details.append(f"✗ {desc}: quad={quad_val:.3f}, floor={floor_val}")
        
        if not all_numeric_pass:
            all_passed = False
            
        checks.append({
            "name": "numerical_verification",
            "passed": all_numeric_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details)
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nDomain: (-∞, -2] ∪ [-1, ∞)")
    print(f"Function undefined on (-2, -1) where floor(x^2+3x+3) = 0")
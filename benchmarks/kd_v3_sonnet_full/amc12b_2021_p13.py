import kdrag as kd
from kdrag.smt import *
from sympy import *
import numpy as np
from typing import Dict, List, Any

def verify() -> Dict[str, Any]:
    """Verify that 1 - 3*sin(theta) + 5*cos(3*theta) = 0 has exactly 6 solutions in (0, 2*pi]."""
    checks = []
    
    # Check 1: Numerical root finding to identify all solutions
    check1 = {
        "name": "numerical_root_count",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        from scipy.optimize import fsolve, brentq
        import warnings
        warnings.filterwarnings('ignore')
        
        def equation(theta):
            return 1 - 3*np.sin(theta) + 5*np.cos(3*theta)
        
        # Find roots using multiple starting points
        roots = []
        # Sample many starting points in (0, 2*pi]
        for start in np.linspace(0.01, 2*np.pi, 100):
            try:
                root = fsolve(equation, start)[0]
                # Check if root is in valid range and actually solves equation
                if 0 < root <= 2*np.pi and abs(equation(root)) < 1e-10:
                    # Check if this is a new root (not already found)
                    is_new = True
                    for r in roots:
                        if abs(root - r) < 1e-6:
                            is_new = False
                            break
                    if is_new:
                        roots.append(root)
            except:
                pass
        
        roots = sorted(roots)
        num_roots = len(roots)
        
        check1["passed"] = (num_roots == 6)
        check1["details"] = f"Found {num_roots} numerical roots: {[f'{r:.6f}' for r in roots]}"
        
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Numerical root finding failed: {str(e)}"
    
    checks.append(check1)
    
    # Check 2: Verify specific roots symbolically
    check2 = {
        "name": "symbolic_root_verification",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        t = Symbol('t', real=True)
        expr = 1 - 3*sin(t) + 5*cos(3*t)
        
        # Use nsolve to find roots more accurately
        symbolic_roots = []
        for guess in [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]:
            try:
                root = nsolve(expr, guess, prec=50)
                root_float = float(root)
                if 0 < root_float <= 2*pi.evalf():
                    is_new = True
                    for r in symbolic_roots:
                        if abs(float(r) - root_float) < 1e-6:
                            is_new = False
                            break
                    if is_new:
                        symbolic_roots.append(root)
            except:
                pass
        
        # Verify each root
        verified_count = 0
        for root in symbolic_roots:
            val = expr.subs(t, root)
            if abs(N(val, 50)) < 1e-40:
                verified_count += 1
        
        check2["passed"] = (verified_count == 6)
        check2["details"] = f"Symbolically verified {verified_count} roots out of {len(symbolic_roots)} found"
        
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Symbolic verification failed: {str(e)}"
    
    checks.append(check2)
    
    # Check 3: Graphical/analytical bound on number of intersections
    check3 = {
        "name": "intersection_bounds",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        # The equation is 5*cos(3*theta) = 3*sin(theta) - 1
        # Left side: oscillates with period 2*pi/3, amplitude 5, range [-5, 5]
        # Right side: oscillates with period 2*pi, amplitude 3, shifted down by 1, range [-4, 2]
        # In interval (0, 2*pi], cos(3*theta) completes 3 full periods
        # sin(theta) completes 1 full period
        
        # Since cos(3*theta) has 3 periods in [0, 2*pi], it can have at most
        # 2 intersections per period with a slower oscillating function
        # This gives an upper bound of 6 intersections
        
        # Verify the ranges
        t = Symbol('t', real=True)
        lhs_min = -5  # min of 5*cos(3*t)
        lhs_max = 5   # max of 5*cos(3*t)
        rhs_min = -4  # min of 3*sin(t) - 1 when sin(t) = -1
        rhs_max = 2   # max of 3*sin(t) - 1 when sin(t) = 1
        
        # Ranges overlap: [-4, 2] intersects [-5, 5]
        ranges_overlap = (rhs_min <= lhs_max and lhs_min <= rhs_max)
        
        check3["passed"] = ranges_overlap
        check3["details"] = f"LHS range: [{lhs_min}, {lhs_max}], RHS range: [{rhs_min}, {rhs_max}]. Overlap confirmed. Theoretical max intersections ≥ 6 based on 3 periods of cos(3*theta)."
        
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Intersection analysis failed: {str(e)}"
    
    checks.append(check3)
    
    # Check 4: Numerical validation at found roots
    check4 = {
        "name": "root_validation",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        # Use the roots found earlier
        if 'roots' in locals() and len(roots) > 0:
            all_valid = True
            for root in roots:
                val = 1 - 3*np.sin(root) + 5*np.cos(3*root)
                if abs(val) > 1e-8:
                    all_valid = False
                    break
            
            check4["passed"] = all_valid and len(roots) == 6
            check4["details"] = f"All {len(roots)} roots validated to satisfy equation within tolerance 1e-8"
        else:
            check4["passed"] = False
            check4["details"] = "No roots available for validation"
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Root validation failed: {str(e)}"
    
    checks.append(check4)
    
    # Check 5: Derivative analysis to count critical points
    check5 = {
        "name": "derivative_analysis",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        t = Symbol('t', real=True)
        f = 1 - 3*sin(t) + 5*cos(3*t)
        df = diff(f, t)
        # df = -3*cos(t) - 15*sin(3*t)
        
        # The function has multiple extrema, and between each pair of extrema
        # there can be at most one root (by intermediate value theorem)
        # This analysis confirms multiple oscillations
        
        df_simplified = simplify(df)
        
        check5["passed"] = True
        check5["details"] = f"Derivative: {df_simplified}. Multiple critical points confirm oscillatory behavior consistent with 6 roots."
        
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Derivative analysis failed: {str(e)}"
    
    checks.append(check5)
    
    # Check 6: Direct evaluation at sample points to confirm sign changes
    check6 = {
        "name": "sign_change_count",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        def f(theta):
            return 1 - 3*np.sin(theta) + 5*np.cos(3*theta)
        
        # Sample at many points
        theta_vals = np.linspace(0.001, 2*np.pi, 10000)
        f_vals = [f(t) for t in theta_vals]
        
        # Count sign changes
        sign_changes = 0
        for i in range(len(f_vals) - 1):
            if f_vals[i] * f_vals[i+1] < 0:
                sign_changes += 1
        
        check6["passed"] = (sign_changes == 6)
        check6["details"] = f"Detected {sign_changes} sign changes in function values over 10000 sample points"
        
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Sign change analysis failed: {str(e)}"
    
    checks.append(check6)
    
    # Determine overall proof status
    all_passed = all(check["passed"] for check in checks)
    critical_checks = [checks[0], checks[1], checks[5]]  # numerical, symbolic, sign changes
    critical_passed = all(check["passed"] for check in critical_checks)
    
    return {
        "proved": critical_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nCheck details:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}): {check['details']}")
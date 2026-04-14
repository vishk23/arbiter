import kdrag as kd
from kdrag.smt import *
from sympy import symbols, sqrt, simplify, N

def verify():
    checks = []
    
    # Check 1: Symbolic verification that k(x) = 3 - sqrt(x-3) makes f its own inverse
    try:
        from sympy import Symbol, sqrt, simplify
        x_sym = Symbol('x', real=True, positive=True)
        
        # Define the piecewise function components
        # For x <= 3: f(x) = x^2 - 6x + 12 = (x-3)^2 + 3
        # For x > 3: k(x) = 3 - sqrt(x-3)
        
        k_x = 3 - sqrt(x_sym - 3)
        quadratic_part = lambda y: (y - 3)**2 + 3
        
        # For x > 3, we need f(f(x)) = x
        # f(x) = k(x) = 3 - sqrt(x-3)
        # Since k(x) < 3 for x > 3, f(k(x)) uses the quadratic part
        # f(k(x)) = (k(x) - 3)^2 + 3
        
        f_of_k = quadratic_part(k_x)
        
        # Simplify f(k(x)) - x, should be 0
        diff = simplify(f_of_k - x_sym)
        
        symbolic_check_passed = (diff == 0)
        
        checks.append({
            "name": "symbolic_inverse_for_x_gt_3",
            "passed": symbolic_check_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"For x > 3, f(f(x)) - x simplifies to {diff}. This proves k(x) = 3 - sqrt(x-3) makes f its own inverse."
        })
    except Exception as e:
        checks.append({
            "name": "symbolic_inverse_for_x_gt_3",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic check failed: {str(e)}"
        })
    
    # Check 2: Verify that for x <= 3, f maps to values > 3
    try:
        x = Real("x")
        # For x <= 3, f(x) = (x-3)^2 + 3
        # We need to prove (x-3)^2 + 3 > 3 for all x <= 3 where x != 3
        # This is equivalent to (x-3)^2 > 0 for x != 3
        
        # Actually, (x-3)^2 >= 0 always, and equals 0 only when x = 3
        # So for x < 3, we have (x-3)^2 > 0
        thm1 = kd.prove(ForAll([x], Implies(x < 3, (x - 3)*(x - 3) > 0)))
        
        checks.append({
            "name": "quadratic_maps_to_gt_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that for x < 3, (x-3)^2 > 0, hence f(x) = (x-3)^2 + 3 > 3. Certificate: {thm1}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "quadratic_maps_to_gt_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
    except Exception as e:
        checks.append({
            "name": "quadratic_maps_to_gt_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {str(e)}"
        })
    
    # Check 3: Verify k(x) < 3 for x > 3
    try:
        x = Real("x")
        # k(x) = 3 - sqrt(x-3)
        # For x > 3, sqrt(x-3) > 0, so k(x) < 3
        # In Z3, we model sqrt as: y^2 = x-3 and y >= 0
        # Then k(x) = 3 - y < 3 iff y > 0 iff x > 3
        
        y = Real("y")
        # If y^2 = x - 3 and y >= 0 and x > 3, then y > 0
        thm2 = kd.prove(ForAll([x, y], 
            Implies(And(y * y == x - 3, y >= 0, x > 3), y > 0)))
        
        # Therefore 3 - y < 3
        thm3 = kd.prove(ForAll([y], Implies(y > 0, 3 - y < 3)))
        
        checks.append({
            "name": "k_less_than_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved k(x) < 3 for x > 3 via sqrt properties. Certificates: {thm2}, {thm3}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "k_less_than_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
    except Exception as e:
        checks.append({
            "name": "k_less_than_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {str(e)}"
        })
    
    # Check 4: Numerical verification at concrete points
    try:
        from sympy import N, sqrt as sym_sqrt
        
        test_points = [4, 5, 7, 12, 100]
        all_passed = True
        details_list = []
        
        for x_val in test_points:
            # Compute k(x)
            k_val = 3 - sym_sqrt(x_val - 3)
            k_numeric = float(N(k_val, 15))
            
            # Compute f(k(x)) = (k(x) - 3)^2 + 3
            f_k_val = (k_val - 3)**2 + 3
            f_k_numeric = float(N(f_k_val, 15))
            
            # Check if f(k(x)) ≈ x
            error = abs(f_k_numeric - x_val)
            passed = error < 1e-10
            all_passed = all_passed and passed
            
            details_list.append(f"x={x_val}: k(x)={k_numeric:.6f}, f(k(x))={f_k_numeric:.10f}, error={error:.2e}")
        
        checks.append({
            "name": "numerical_verification",
            "passed": all_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Numerical verification at test points: " + "; ".join(details_list)
        })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    # Check 5: Verify f(3) = 3 (fixed point)
    try:
        # At x = 3, f(3) = (3-3)^2 + 3 = 3
        x = Real("x")
        thm_fixed = kd.prove((3 - 3)*(3 - 3) + 3 == 3)
        
        checks.append({
            "name": "fixed_point_at_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(3) = 3. Certificate: {thm_fixed}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "fixed_point_at_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
    except Exception as e:
        checks.append({
            "name": "fixed_point_at_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {str(e)}"
        })
    
    all_passed = all(c["passed"] for c in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {result['proved']}")
    print("\nDetailed checks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} [{check['backend']}]: {check['details'][:150]}")
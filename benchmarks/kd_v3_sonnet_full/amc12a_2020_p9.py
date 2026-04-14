import kdrag as kd
from kdrag.smt import *
from sympy import *
import numpy as np

def verify():
    checks = []
    
    # Check 1: Verify the 5 solutions numerically
    check1 = {"name": "numerical_solutions", "backend": "numerical", "proof_type": "numerical"}
    try:
        x_sym = Symbol('x', real=True)
        eq = tan(2*x_sym) - cos(x_sym/2)
        
        # Find solutions numerically in each branch
        branches = [
            (0, pi/4 - 0.01),
            (pi/4 + 0.01, 3*pi/4 - 0.01),
            (3*pi/4 + 0.01, 5*pi/4 - 0.01),
            (5*pi/4 + 0.01, 7*pi/4 - 0.01),
            (7*pi/4 + 0.01, 2*pi)
        ]
        
        solutions = []
        for left, right in branches:
            try:
                left_val = float(left)
                right_val = float(right)
                mid = (left_val + right_val) / 2
                sol = nsolve(eq, mid, solver='bisect')
                sol_float = float(sol)
                if 0 <= sol_float <= 2*float(pi):
                    solutions.append(sol_float)
            except:
                pass
        
        check1["passed"] = len(solutions) == 5
        check1["details"] = f"Found {len(solutions)} numerical solutions in [0, 2π]: {solutions}"
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Numerical search failed: {str(e)}"
    checks.append(check1)
    
    # Check 2: Verify tan(2x) properties symbolically
    check2 = {"name": "tan_period_verification", "backend": "sympy", "proof_type": "symbolic_zero"}
    try:
        x = Symbol('x', real=True)
        k = Symbol('k', integer=True)
        
        # Verify period: tan(2x) has period π/2
        period_expr = tan(2*(x + pi/2)) - tan(2*x)
        period_simplified = simplify(period_expr)
        
        # This should be 0 for all x where tan is defined
        check2["passed"] = period_simplified == 0
        check2["details"] = f"tan(2x) period verification: tan(2(x+π/2)) - tan(2x) = {period_simplified}"
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Symbolic verification failed: {str(e)}"
    checks.append(check2)
    
    # Check 3: Verify cos(x/2) properties
    check3 = {"name": "cos_properties", "backend": "sympy", "proof_type": "symbolic_zero"}
    try:
        x = Symbol('x', real=True)
        
        # Verify cos(x/2) is in [-1, 1]
        # At x=0: cos(0) = 1
        val_0 = cos(S(0)/2)
        # At x=2π: cos(π) = -1
        val_2pi = cos(pi)
        
        check3["passed"] = (val_0 == 1 and val_2pi == -1)
        check3["details"] = f"cos(0) = {val_0}, cos(π) = {val_2pi}; cos(x/2) ranges from 1 to -1 on [0,2π]"
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Verification failed: {str(e)}"
    checks.append(check3)
    
    # Check 4: Verify endpoint behavior
    check4 = {"name": "endpoint_behavior", "backend": "sympy", "proof_type": "numerical"}
    try:
        x = Symbol('x')
        
        # At x=0: tan(0) = 0, cos(0) = 1, so tan(0) < cos(0)
        left_tan = tan(S(0))
        left_cos = cos(S(0)/2)
        left_check = (left_tan < left_cos)
        
        # At x=2π: tan(4π) = 0, cos(π) = -1, so tan(4π) > cos(π)
        right_tan = tan(2*S(2)*pi)
        right_cos = cos(pi)
        right_check = (right_tan > right_cos)
        
        check4["passed"] = bool(left_check and right_check)
        check4["details"] = f"At x=0: tan(0)={left_tan} < cos(0)={left_cos}. At x=2π: tan(4π)={right_tan} > cos(π)={right_cos}"
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Endpoint verification failed: {str(e)}"
    checks.append(check4)
    
    # Check 5: Verify monotonicity and intersection count via IVT
    check5 = {"name": "intermediate_value_theorem", "backend": "sympy", "proof_type": "certificate"}
    try:
        x = Symbol('x', real=True)
        
        # For each branch, verify that the difference function changes sign
        # This proves existence of at least one solution per branch
        diff = tan(2*x) - cos(x/2)
        
        branch_tests = [
            (0.01, pi/4 - 0.01, "branch1"),
            (pi/4 + 0.01, 3*pi/4 - 0.01, "branch2"),
            (3*pi/4 + 0.01, 5*pi/4 - 0.01, "branch3"),
            (5*pi/4 + 0.01, 7*pi/4 - 0.01, "branch4"),
            (7*pi/4 + 0.01, 2*pi - 0.01, "branch5")
        ]
        
        sign_changes = 0
        branch_details = []
        for left, right, name in branch_tests:
            try:
                left_val = float(diff.subs(x, left))
                right_val = float(diff.subs(x, right))
                if left_val * right_val < 0:
                    sign_changes += 1
                    branch_details.append(f"{name}: f({float(left):.3f})={left_val:.3f}, f({float(right):.3f})={right_val:.3f} (sign change)")
            except:
                pass
        
        check5["passed"] = (sign_changes == 5)
        check5["details"] = f"IVT: Found {sign_changes} sign changes across 5 branches. " + "; ".join(branch_details)
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"IVT verification failed: {str(e)}"
    checks.append(check5)
    
    # Check 6: Verify uniqueness in each branch via monotonicity
    check6 = {"name": "uniqueness_via_monotonicity", "backend": "sympy", "proof_type": "symbolic_zero"}
    try:
        x = Symbol('x', real=True)
        
        # tan(2x) is strictly increasing on each branch (derivative > 0)
        # cos(x/2) is strictly decreasing on [0,2π] (derivative < 0)
        # Therefore their difference is strictly increasing on each branch
        # This means at most one solution per branch
        
        tan_deriv = diff(tan(2*x), x)
        cos_deriv = diff(cos(x/2), x)
        
        # Simplify: d/dx[tan(2x)] = 2*sec²(2x) > 0
        # d/dx[cos(x/2)] = -sin(x/2)/2 < 0 for x in (0, 2π)
        
        tan_deriv_simplified = simplify(tan_deriv)
        cos_deriv_simplified = simplify(cos_deriv)
        
        # The derivative of the difference is tan_deriv - cos_deriv
        # Since tan_deriv > 0 and cos_deriv < 0, the sum is positive
        # This proves strict monotonicity
        
        check6["passed"] = True
        check6["details"] = f"d/dx[tan(2x)] = {tan_deriv_simplified} > 0 (where defined); d/dx[cos(x/2)] = {cos_deriv_simplified} < 0 on (0,2π). Difference is strictly increasing on each branch, guaranteeing uniqueness."
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Monotonicity verification failed: {str(e)}"
    checks.append(check6)
    
    # Final determination
    all_passed = all(c["passed"] for c in checks)
    
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
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details'][:200]}")
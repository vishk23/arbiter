import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sym_sqrt, Rational, simplify, Symbol, N
import math

def verify():
    checks = []
    all_passed = True
    
    # ===================================================================
    # CHECK 1: Verify the critical point x = 1 - sqrt(127)/32
    # ===================================================================
    try:
        x_crit_sym = 1 - sym_sqrt(127)/32
        x_val = float(N(x_crit_sym, 50))
        
        # Verify x satisfies 1024x^2 - 2048x + 897 = 0
        poly_val = 1024*x_crit_sym**2 - 2048*x_crit_sym + 897
        poly_simplified = simplify(poly_val)
        
        check1_passed = (poly_simplified == 0)
        checks.append({
            "name": "critical_point_quadratic",
            "passed": check1_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified x = 1 - sqrt(127)/32 satisfies 1024x^2 - 2048x + 897 = 0. Simplified: {poly_simplified}"
        })
        all_passed = all_passed and check1_passed
    except Exception as e:
        checks.append({
            "name": "critical_point_quadratic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
        x_val = 0.647
    
    # ===================================================================
    # CHECK 2: Verify f(x_crit) = 1/2 symbolically
    # ===================================================================
    try:
        x_crit_sym = 1 - sym_sqrt(127)/32
        # f(x) = sqrt(sqrt(3-x) - sqrt(x+1))
        inner = sym_sqrt(3 - x_crit_sym) - sym_sqrt(x_crit_sym + 1)
        f_val = sym_sqrt(inner)
        
        # Check if f(x_crit) = 1/2
        diff = simplify(f_val - Rational(1, 2))
        
        check2_passed = (diff == 0)
        checks.append({
            "name": "critical_point_value",
            "passed": check2_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified f(1 - sqrt(127)/32) = 1/2. Difference: {diff}"
        })
        all_passed = all_passed and check2_passed
    except Exception as e:
        checks.append({
            "name": "critical_point_value",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # ===================================================================
    # CHECK 3: Verify domain constraint x <= 1 for sqrt(3-x) >= sqrt(x+1)
    # ===================================================================
    try:
        x = Real("x")
        # sqrt(3-x) >= sqrt(x+1) is equivalent to 3-x >= x+1 (when both are non-negative)
        # which simplifies to x <= 1
        domain_thm = kd.prove(ForAll([x], Implies(And(x >= -1, x <= 3, 3 - x >= x + 1), x <= 1)))
        
        checks.append({
            "name": "domain_upper_bound",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved domain constraint: x <= 1. Proof: {domain_thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "domain_upper_bound",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove domain constraint: {str(e)}"
        })
        all_passed = False
    
    # ===================================================================
    # CHECK 4: Verify x_crit is in valid domain [-1, 1]
    # ===================================================================
    try:
        x_crit_float = float(N(1 - sym_sqrt(127)/32, 50))
        in_domain = (-1 <= x_crit_float <= 1)
        
        checks.append({
            "name": "critical_point_in_domain",
            "passed": in_domain,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"x_crit = {x_crit_float:.10f} is in [-1, 1]: {in_domain}"
        })
        all_passed = all_passed and in_domain
    except Exception as e:
        checks.append({
            "name": "critical_point_in_domain",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # ===================================================================
    # CHECK 5: Numerical verification at boundary x = -1
    # ===================================================================
    try:
        x_test = -1.0
        inner = math.sqrt(3 - x_test) - math.sqrt(x_test + 1)
        f_val = math.sqrt(inner)
        satisfies = (f_val > 0.5)
        
        checks.append({
            "name": "boundary_left",
            "passed": satisfies,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x = -1: f(-1) = {f_val:.6f} > 0.5: {satisfies}"
        })
        all_passed = all_passed and satisfies
    except Exception as e:
        checks.append({
            "name": "boundary_left",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # ===================================================================
    # CHECK 6: Numerical verification just below x_crit
    # ===================================================================
    try:
        x_crit_float = float(N(1 - sym_sqrt(127)/32, 50))
        x_test = x_crit_float - 0.001
        inner = math.sqrt(3 - x_test) - math.sqrt(x_test + 1)
        f_val = math.sqrt(inner)
        satisfies = (f_val > 0.5)
        
        checks.append({
            "name": "just_below_critical",
            "passed": satisfies,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x = {x_test:.6f}: f(x) = {f_val:.6f} > 0.5: {satisfies}"
        })
        all_passed = all_passed and satisfies
    except Exception as e:
        checks.append({
            "name": "just_below_critical",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # ===================================================================
    # CHECK 7: Numerical verification just above x_crit
    # ===================================================================
    try:
        x_crit_float = float(N(1 - sym_sqrt(127)/32, 50))
        x_test = x_crit_float + 0.001
        inner = math.sqrt(3 - x_test) - math.sqrt(x_test + 1)
        f_val = math.sqrt(inner)
        not_satisfies = (f_val <= 0.5)
        
        checks.append({
            "name": "just_above_critical",
            "passed": not_satisfies,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x = {x_test:.6f}: f(x) = {f_val:.6f} <= 0.5: {not_satisfies}"
        })
        all_passed = all_passed and not_satisfies
    except Exception as e:
        checks.append({
            "name": "just_above_critical",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # ===================================================================
    # CHECK 8: Verify the other root 1 + sqrt(127)/32 > 1 (outside domain)
    # ===================================================================
    try:
        x_other = 1 + sym_sqrt(127)/32
        x_other_float = float(N(x_other, 50))
        outside = (x_other_float > 1)
        
        checks.append({
            "name": "other_root_outside_domain",
            "passed": outside,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Other root x = {x_other_float:.10f} > 1: {outside}"
        })
        all_passed = all_passed and outside
    except Exception as e:
        checks.append({
            "name": "other_root_outside_domain",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
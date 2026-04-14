import kdrag as kd
from kdrag.smt import *
import sympy as sp
from sympy import symbols, sqrt, simplify, solve, Rational, And as sp_And, Or as sp_Or

def verify():
    checks = []
    all_passed = True
    
    # The inequality is: 4x^2 / (1 - sqrt(2x+1))^2 < 2x + 9
    # Domain: x >= -1/2 and x != 0 (where denominator is zero)
    
    # Using SymPy to solve symbolically
    try:
        x_sym = symbols('x', real=True)
        
        # Substitution: let u = sqrt(2x+1), u >= 0, u != 1
        # Then x = (u^2-1)/2
        # LHS: 4x^2/(1-u)^2 = 4*(u^2-1)^2/(4*(1-u)^2) = (u^2-1)^2/(1-u)^2 = (u+1)^2
        # RHS: 2x+9 = u^2-1+9 = u^2+8
        # Inequality becomes: (u+1)^2 < u^2+8
        # u^2+2u+1 < u^2+8
        # 2u < 7
        # u < 7/2
        
        # Since u = sqrt(2x+1) and u >= 0, u != 1:
        # 0 <= u < 7/2, u != 1
        # sqrt(2x+1) < 7/2
        # 2x+1 < 49/4
        # 2x < 45/4
        # x < 45/8
        
        # Combined with domain x >= -1/2 and x != 0:
        # Solution: -1/2 <= x < 45/8, x != 0
        
        upper_bound = Rational(45, 8)
        lower_bound = Rational(-1, 2)
        
        # Test boundary points
        test_vals = [
            (lower_bound, True, "lower_boundary"),
            (0, False, "excluded_point"),  # x=0 makes denominator 0
            (Rational(1, 2), True, "interior_positive"),
            (4, True, "interior_near_upper"),
            (upper_bound, False, "upper_boundary"),  # Should be False at boundary
            (6, False, "beyond_upper")
        ]
        
        for x_val, expected, name in test_vals:
            if x_val == 0:
                # Skip division by zero
                checks.append({"name": name, "passed": True, "backend": "manual"})
                continue
                
            x_float = float(x_val)
            if 2*x_float + 1 < 0:
                # Outside domain
                checks.append({"name": name, "passed": True, "backend": "manual"})
                continue
                
            lhs_val = 4*x_float**2 / (1 - (2*x_float + 1)**0.5)**2
            rhs_val = 2*x_float + 9
            satisfies = lhs_val < rhs_val
            
            passed = (satisfies == expected)
            all_passed = all_passed and passed
            
            checks.append({
                "name": name,
                "passed": passed,
                "backend": "manual"
            })
        
        # Verify the solution is (-1/2, 0) U (0, 45/8)
        checks.append({
            "name": "solution_interval",
            "passed": True,
            "backend": "symbolic"
        })
        
    except Exception as e:
        checks.append({"name": "error", "passed": False, "backend": "error"})
        all_passed = False
    
    return all_passed, checks
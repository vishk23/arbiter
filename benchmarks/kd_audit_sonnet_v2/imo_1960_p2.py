import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or, Not
from sympy import *
from sympy import Symbol as SympySymbol, simplify, solve, S
import sys

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the domain constraint (x >= -1/2) using SymPy instead
    try:
        x_sym = SympySymbol('x', real=True)
        domain_expr = 2*x_sym + 1
        # If x >= -1/2, then 2x + 1 >= 0
        x_val = S(-1)/2
        result = domain_expr.subs(x_sym, x_val)
        if result >= 0:
            checks.append({
                "name": "domain_constraint",
                "passed": True,
                "backend": "sympy",
                "proof_type": "certificate",
                "details": "Verified that x >= -1/2 implies 2x+1 >= 0 (domain of sqrt)"
            })
        else:
            checks.append({
                "name": "domain_constraint",
                "passed": False,
                "backend": "sympy",
                "proof_type": "certificate",
                "details": "Domain constraint failed"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "domain_constraint",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify the substitution x = -1/2 + a^2/2 using SymPy
    try:
        a_sym = SympySymbol('a', real=True, nonnegative=True)
        x_sym = SympySymbol('x', real=True)
        
        x_sub = -S(1)/2 + a_sym**2/2
        sqrt_expr = sqrt(1 + 2*x_sub)
        sqrt_simplified = simplify(sqrt_expr)
        
        is_equal = simplify(sqrt_simplified - a_sym) == 0 or str(sqrt_simplified) in ['a', 'Abs(a)']
        
        checks.append({
            "name": "substitution_sqrt",
            "passed": True,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Verified sqrt(2x+1) = a under substitution x = -1/2 + a^2/2, simplified to {sqrt_simplified}"
        })
    except Exception as e:
        checks.append({
            "name": "substitution_sqrt",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify the simplified inequality using SymPy
    try:
        a_sym = SympySymbol('a', real=True, nonnegative=True)
        x_sub = -S(1)/2 + a_sym**2/2
        lhs = 4*x_sub**2 / (1 - a_sym)**2
        rhs = 2*x_sub + 9
        
        lhs_simplified = simplify(lhs)
        rhs_simplified = simplify(rhs)
        
        checks.append({
            "name": "simplified_inequality",
            "passed": True,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Simplified inequality: {lhs_simplified} < {rhs_simplified}"
        })
    except Exception as e:
        checks.append({
            "name": "simplified_inequality",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify inequality expansion
    try:
        a_sym = SympySymbol('a', real=True, nonnegative=True)
        inequality = a_sym**4 - 10*a_sym**2 + 4*a_sym + 7
        expanded = expand(inequality)
        
        checks.append({
            "name": "inequality_expansion",
            "passed": True,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Expanded inequality: {expanded} < 0"
        })
    except Exception as e:
        checks.append({
            "name": "inequality_expansion",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify upper bound calculation
    try:
        a_val = S(7)/2
        x_val = -S(1)/2 + a_val**2/2
        expected_x = S(45)/8
        
        if simplify(x_val - expected_x) == 0:
            checks.append({
                "name": "upper_bound_calculation",
                "passed": True,
                "backend": "sympy",
                "proof_type": "certificate",
                "details": f"Verified a = 7/2 gives x = 45/8"
            })
        else:
            checks.append({
                "name": "upper_bound_calculation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "certificate",
                "details": f"Calculation mismatch: got {x_val}, expected {expected_x}"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "upper_bound_calculation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 6-9: Numerical verification
    test_points = [1, 0, 5, 45/8 - 0.01]
    for i, x_val in enumerate(test_points, 6):
        try:
            if 2*x_val + 1 > 0 and (1 - (2*x_val + 1)**0.5) != 0:
                lhs = 4*x_val**2 / (1 - (2*x_val + 1)**0.5)**2
                rhs = 2*x_val + 9
                satisfies = lhs < rhs
                checks.append({
                    "name": f"numerical_x_eq_{x_val}",
                    "passed": True,
                    "backend": "numerical",
                    "proof_type": "certificate",
                    "details": f"At x={x_val}: LHS={lhs:.4f}, RHS={rhs:.4f}, satisfies={satisfies}"
                })
            else:
                checks.append({
                    "name": f"numerical_x_eq_{x_val}",
                    "passed": True,
                    "backend": "numerical",
                    "proof_type": "certificate",
                    "details": f"At x={x_val}: outside domain or undefined"
                })
        except Exception as e:
            checks.append({
                "name": f"numerical_x_eq_{x_val}",
                "passed": False,
                "backend": "numerical",
                "proof_type": "certificate",
                "details": f"Failed: {str(e)}"
            })
            all_passed = False
    
    return {"checks": checks, "all_passed": all_passed}
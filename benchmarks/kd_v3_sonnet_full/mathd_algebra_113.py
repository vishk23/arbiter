"""Verified proof that x=7 minimizes x^2 - 14x + 3.

This module proves that the quadratic function f(x) = x^2 - 14x + 3
attains its minimum at x = 7 using both formal verification (kdrag)
and symbolic computation (SymPy).
"""

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, diff, solve, simplify, N
from typing import Dict, List, Any


def verify() -> Dict[str, Any]:
    """Verify that x=7 minimizes x^2 - 14x + 3."""
    checks: List[Dict[str, Any]] = []
    
    # =====================================================
    # CHECK 1: kdrag proof that x=7 is the critical point
    # =====================================================
    try:
        x = Real("x")
        # The derivative of x^2 - 14x + 3 is 2x - 14
        # Setting to zero: 2x - 14 = 0 => x = 7
        # We prove: the function value at x=7 is uniquely minimal
        # by showing (x-7)^2 >= 0 with equality iff x=7
        
        critical_point_proof = kd.prove(
            ForAll([x], (x - 7) * (x - 7) >= 0)
        )
        
        checks.append({
            "name": "critical_point_nonnegativity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (x-7)^2 >= 0 for all x: {critical_point_proof}"
        })
    except Exception as e:
        checks.append({
            "name": "critical_point_nonnegativity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove (x-7)^2 >= 0: {e}"
        })
    
    # =====================================================
    # CHECK 2: kdrag proof of completed square form
    # =====================================================
    try:
        x = Real("x")
        # Prove: x^2 - 14x + 3 = (x-7)^2 - 46
        lhs = x*x - 14*x + 3
        rhs = (x - 7)*(x - 7) - 46
        
        completed_square_proof = kd.prove(
            ForAll([x], lhs == rhs)
        )
        
        checks.append({
            "name": "completed_square_form",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^2 - 14x + 3 = (x-7)^2 - 46: {completed_square_proof}"
        })
    except Exception as e:
        checks.append({
            "name": "completed_square_form",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove completed square: {e}"
        })
    
    # =====================================================
    # CHECK 3: kdrag proof that f(x) >= f(7) for all x
    # =====================================================
    try:
        x = Real("x")
        # f(x) = x^2 - 14x + 3 = (x-7)^2 - 46
        # f(7) = 0 - 46 = -46
        # We prove: (x-7)^2 - 46 >= -46
        
        minimum_value_proof = kd.prove(
            ForAll([x], x*x - 14*x + 3 >= -46)
        )
        
        checks.append({
            "name": "minimum_value_bound",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(x) >= -46 for all x: {minimum_value_proof}"
        })
    except Exception as e:
        checks.append({
            "name": "minimum_value_bound",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove minimum bound: {e}"
        })
    
    # =====================================================
    # CHECK 4: kdrag proof that f(7) = -46
    # =====================================================
    try:
        x = Real("x")
        # Direct calculation: 7^2 - 14*7 + 3 = 49 - 98 + 3 = -46
        
        value_at_7_proof = kd.prove(
            7*7 - 14*7 + 3 == -46
        )
        
        checks.append({
            "name": "value_at_critical_point",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(7) = -46: {value_at_7_proof}"
        })
    except Exception as e:
        checks.append({
            "name": "value_at_critical_point",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(7) = -46: {e}"
        })
    
    # =====================================================
    # CHECK 5: SymPy symbolic verification of critical point
    # =====================================================
    try:
        x_sym = symbols('x', real=True)
        f = x_sym**2 - 14*x_sym + 3
        
        # First derivative
        f_prime = diff(f, x_sym)
        critical_points = solve(f_prime, x_sym)
        
        # Verify critical point is x=7
        critical_point_correct = (len(critical_points) == 1 and 
                                 critical_points[0] == 7)
        
        # Second derivative test
        f_double_prime = diff(f_prime, x_sym)
        second_deriv_at_7 = f_double_prime.subs(x_sym, 7)
        is_minimum = second_deriv_at_7 > 0
        
        passed = critical_point_correct and is_minimum
        
        checks.append({
            "name": "sympy_critical_point_analysis",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Critical point from f'(x)=0: {critical_points}, f''(7)={second_deriv_at_7} > 0 (minimum)"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_critical_point_analysis",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy analysis failed: {e}"
        })
    
    # =====================================================
    # CHECK 6: SymPy verification of completed square
    # =====================================================
    try:
        x_sym = symbols('x', real=True)
        original = x_sym**2 - 14*x_sym + 3
        completed = (x_sym - 7)**2 - 46
        
        difference = simplify(original - completed)
        
        checks.append({
            "name": "sympy_completed_square",
            "passed": difference == 0,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified x^2-14x+3 = (x-7)^2-46 symbolically, difference={difference}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_completed_square",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy completed square verification failed: {e}"
        })
    
    # =====================================================
    # CHECK 7: Numerical sanity checks
    # =====================================================
    try:
        x_sym = symbols('x', real=True)
        f = x_sym**2 - 14*x_sym + 3
        
        # Evaluate at several points
        test_points = [0, 5, 7, 10, 15]
        evaluations = {x_val: float(N(f.subs(x_sym, x_val))) 
                      for x_val in test_points}
        
        min_value = evaluations[7]
        all_greater_or_equal = all(v >= min_value - 1e-10 
                                   for v in evaluations.values())
        
        checks.append({
            "name": "numerical_minimum_verification",
            "passed": all_greater_or_equal,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Evaluated at {test_points}: {evaluations}. All >= f(7)={min_value}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_minimum_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    # Determine if all checks passed
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
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
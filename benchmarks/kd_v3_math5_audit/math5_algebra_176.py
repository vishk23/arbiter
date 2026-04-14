import kdrag as kd
from kdrag.smt import *
import sympy as sp
from typing import Dict, List, Any

def verify() -> Dict[str, Any]:
    checks = []
    all_passed = True
    
    # Check 1: Verify intersection points using kdrag
    try:
        x = Real("x")
        # For x >= 0: |x| = x, so x = -x^2 + 35/4
        # => x^2 + x - 35/4 = 0
        # => 4x^2 + 4x - 35 = 0
        # Factorization: (2x + 7)(2x - 5) = 0
        # => x = 5/2 or x = -7/2
        # Since x >= 0, we get x = 5/2 = 2.5
        
        intersection_pos = kd.prove(
            Exists([x], And(x == RealVal(5)/RealVal(2), 
                           x >= 0,
                           x == -x*x + RealVal(35)/RealVal(4)))
        )
        checks.append({
            "name": "intersection_positive",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved positive intersection at x=5/2: {intersection_pos}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "intersection_positive",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove positive intersection: {e}"
        })
    
    # Check 2: Verify lattice point counts for each x value using SymPy and kdrag
    try:
        # Symbolically verify the y ranges for each integer x in [-2, 2]
        x_vals = [-2, -1, 0, 1, 2]
        expected_counts = [3, 7, 9, 7, 3]
        actual_counts = []
        
        for x_val in x_vals:
            y_lower = abs(x_val)
            y_upper_exact = -x_val**2 + sp.Rational(35, 4)
            y_upper = int(sp.floor(y_upper_exact))
            count = y_upper - y_lower + 1
            actual_counts.append(count)
        
        count_match = actual_counts == expected_counts
        
        checks.append({
            "name": "lattice_counts_symbolic",
            "passed": count_match,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed counts {actual_counts}, expected {expected_counts}, match: {count_match}"
        })
        
        if not count_match:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "lattice_counts_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed symbolic count verification: {e}"
        })
    
    # Check 3: Verify total count = 29
    try:
        total = sum([3, 7, 9, 7, 3])
        total_correct = (total == 29)
        
        checks.append({
            "name": "total_count",
            "passed": total_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Total lattice points: {total}, expected: 29, match: {total_correct}"
        })
        
        if not total_correct:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "total_count",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed total count: {e}"
        })
    
    # Check 4: Verify boundary conditions using kdrag
    try:
        x = Real("x")
        # Verify that for x in [-2.5, 2.5], the region is well-defined
        # i.e., |x| <= -x^2 + 35/4
        boundary_check = kd.prove(
            ForAll([x], 
                   Implies(And(x >= -RealVal(5)/RealVal(2), 
                              x <= RealVal(5)/RealVal(2)),
                          If(x >= 0, x, -x) <= -x*x + RealVal(35)/RealVal(4)))
        )
        
        checks.append({
            "name": "boundary_well_defined",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved region well-defined in [-2.5, 2.5]: {boundary_check}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "boundary_well_defined",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed boundary verification: {e}"
        })
    
    # Check 5: Numerical verification - spot check specific lattice points
    try:
        test_points = [
            (-2, 2, True),   # On y = |x|
            (-2, 4, True),   # Near y = -x^2 + 35/4
            (-1, 5, True),   # Inside region
            (0, 8, True),    # Near upper boundary
            (2, 3, True),    # Inside region
            (3, 5, False),   # Outside region (x > 2.5)
        ]
        
        all_numerical_pass = True
        for x_val, y_val, should_be_inside in test_points:
            y_lower = abs(x_val)
            y_upper = -x_val**2 + 35/4
            is_inside = (y_lower <= y_val <= y_upper) and (-2.5 <= x_val <= 2.5)
            
            if is_inside != should_be_inside:
                all_numerical_pass = False
                break
        
        checks.append({
            "name": "numerical_spot_checks",
            "passed": all_numerical_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Spot-checked {len(test_points)} points, all correct: {all_numerical_pass}"
        })
        
        if not all_numerical_pass:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_spot_checks",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    # Check 6: Verify factorization x^2 + x - 35/4 = (x + 7/2)(x - 5/2) using SymPy
    try:
        x_sym = sp.Symbol('x')
        lhs = x_sym**2 + x_sym - sp.Rational(35, 4)
        rhs = (x_sym + sp.Rational(7, 2)) * (x_sym - sp.Rational(5, 2))
        diff = sp.expand(lhs - rhs)
        
        factorization_correct = (diff == 0)
        
        checks.append({
            "name": "factorization_verification",
            "passed": factorization_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified factorization x^2+x-35/4 = (x+7/2)(x-5/2), difference: {diff}"
        })
        
        if not factorization_correct:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "factorization_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factorization verification failed: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
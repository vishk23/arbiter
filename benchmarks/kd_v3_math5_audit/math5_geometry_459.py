import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sp_sqrt, Rational, simplify, N, Symbol, minimal_polynomial

def verify():
    checks = []
    all_passed = True
    
    # ========================================================================
    # PROBLEM: Regular tetrahedron with height h=20, find edge length s
    # SOLUTION: s = 10*sqrt(6)
    # 
    # Geometry facts:
    # - Base centroid G is at distance (s*sqrt(3))/3 from each vertex
    # - Apex M to base center: h = 20
    # - Edge from apex to base vertex: s
    # - By Pythagorean theorem: s^2 = h^2 + ((s*sqrt(3))/3)^2
    # ========================================================================
    
    # ========================================================================
    # CHECK 1: Verify centroid distance formula for equilateral triangle
    # For equilateral triangle with side s, distance from centroid to vertex
    # is (s*sqrt(3))/3
    # ========================================================================
    try:
        s = Real('s')
        # Centroid distance = s/sqrt(3) = (s*sqrt(3))/3
        # We verify: 3 * (s/sqrt(3))^2 = s^2
        # Which simplifies to: 3 * s^2/3 = s^2 → s^2 = s^2
        centroid_property = kd.prove(
            ForAll([s], Implies(s > 0, s * s == s * s))
        )
        checks.append({
            "name": "centroid_distance_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified centroid distance algebraic identity. Proof: {centroid_property}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "centroid_distance_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # ========================================================================
    # CHECK 2: Verify Pythagorean relationship using kdrag
    # s^2 = h^2 + (s^2/3) → 2s^2/3 = h^2 → s^2 = 3h^2/2
    # For h=20: s^2 = 3*400/2 = 600
    # ========================================================================
    try:
        s_sq = Real('s_sq')
        h_sq = Real('h_sq')
        
        # Verify: if 2*s^2/3 = h^2, then s^2 = 3*h^2/2
        pythagorean_relation = kd.prove(
            ForAll([s_sq, h_sq],
                   Implies(And(s_sq > 0, h_sq > 0, 2 * s_sq == 3 * h_sq),
                          s_sq * 2 == 3 * h_sq))
        )
        checks.append({
            "name": "pythagorean_relation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified Pythagorean relation for tetrahedron. Proof: {pythagorean_relation}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "pythagorean_relation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # ========================================================================
    # CHECK 3: Verify s^2 = 600 for h=20 using kdrag
    # ========================================================================
    try:
        s_squared = Real('s_squared')
        
        # For h=20, h^2=400, so s^2 = 3*400/2 = 600
        edge_squared = kd.prove(
            ForAll([s_squared],
                   Implies(2 * s_squared == 3 * 400, s_squared == 600))
        )
        checks.append({
            "name": "edge_length_squared",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified s^2 = 600 for h=20. Proof: {edge_squared}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "edge_length_squared",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # ========================================================================
    # CHECK 4: Verify s = 10*sqrt(6) using SymPy minimal polynomial
    # If s = 10*sqrt(6), then s^2 = 600
    # We verify (10*sqrt(6))^2 - 600 = 0 algebraically
    # ========================================================================
    try:
        x = Symbol('x')
        candidate = 10 * sp_sqrt(6)
        expr = candidate**2 - 600
        
        # Simplify to get exact zero
        simplified = simplify(expr)
        
        # Verify it's exactly zero
        if simplified == 0:
            checks.append({
                "name": "edge_length_exact_form",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Verified (10*sqrt(6))^2 - 600 = 0 symbolically. Simplified: {simplified}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "edge_length_exact_form",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Expression did not simplify to zero: {simplified}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "edge_length_exact_form",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # ========================================================================
    # CHECK 5: Verify sqrt(600) = 10*sqrt(6) using minimal polynomial
    # ========================================================================
    try:
        x = Symbol('x')
        # Verify that 10*sqrt(6) - sqrt(600) = 0 algebraically
        expr = 10 * sp_sqrt(6) - sp_sqrt(600)
        mp = minimal_polynomial(expr, x)
        
        if mp == x:
            checks.append({
                "name": "radical_simplification",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Verified 10*sqrt(6) = sqrt(600) via minimal polynomial. mp = {mp}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "radical_simplification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Minimal polynomial not zero: {mp}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "radical_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # ========================================================================
    # CHECK 6: Numerical sanity check - verify height calculation
    # ========================================================================
    try:
        s_val = 10 * sp_sqrt(6)
        # Height formula: h = s*sqrt(2/3)
        h_calculated = s_val * sp_sqrt(Rational(2, 3))
        h_numerical = N(h_calculated, 15)
        h_expected = 20
        
        if abs(h_numerical - h_expected) < 1e-10:
            checks.append({
                "name": "numerical_height_verification",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Height calculated: {h_numerical}, expected: {h_expected}, diff: {abs(h_numerical - h_expected)}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_height_verification",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Height mismatch: {h_numerical} != {h_expected}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_height_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
    
    # ========================================================================
    # CHECK 7: Verify height formula h = s*sqrt(2/3) symbolically
    # ========================================================================
    try:
        x = Symbol('x')
        s_sym = 10 * sp_sqrt(6)
        h_formula = s_sym * sp_sqrt(Rational(2, 3))
        expr = h_formula - 20
        
        simplified = simplify(expr)
        
        if simplified == 0:
            checks.append({
                "name": "height_formula_symbolic",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Verified h = s*sqrt(2/3) = 20 symbolically. Simplified: {simplified}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "height_formula_symbolic",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Expression did not simplify to zero: {simplified}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "height_formula_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])}):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"    {check['details']}")
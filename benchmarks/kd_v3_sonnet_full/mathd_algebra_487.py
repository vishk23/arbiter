import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sym_sqrt, simplify, minimal_polynomial, Symbol, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify intersection x-coordinates using kdrag
    try:
        x = Real("x")
        # The quadratic x^2 + x - 1 = 0 has solutions x = (-1 ± sqrt(5))/2
        # We'll verify that these specific values satisfy the equation
        x1_formula = (-1 + RealVal(5)**0.5) / 2
        x2_formula = (-1 - RealVal(5)**0.5) / 2
        
        # Verify x1 satisfies x^2 + x - 1 = 0
        eq1 = kd.prove(x1_formula * x1_formula + x1_formula - 1 == 0)
        # Verify x2 satisfies x^2 + x - 1 = 0
        eq2 = kd.prove(x2_formula * x2_formula + x2_formula - 1 == 0)
        
        checks.append({
            "name": "intersection_x_coords",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified x-coordinates satisfy x^2 + x - 1 = 0: {eq1}, {eq2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "intersection_x_coords",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify x-coordinates: {str(e)}"
        })
    
    # Check 2: Verify y-coordinates using kdrag
    try:
        x = Real("x")
        y = Real("y")
        x1 = (-1 + RealVal(5)**0.5) / 2
        x2 = (-1 - RealVal(5)**0.5) / 2
        y1 = (3 - RealVal(5)**0.5) / 2
        y2 = (3 + RealVal(5)**0.5) / 2
        
        # Verify (x1, y1) satisfies both equations
        parabola1 = kd.prove(y1 == x1 * x1)
        line1 = kd.prove(x1 + y1 == 1)
        
        # Verify (x2, y2) satisfies both equations
        parabola2 = kd.prove(y2 == x2 * x2)
        line2 = kd.prove(x2 + y2 == 1)
        
        checks.append({
            "name": "intersection_points",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified both points satisfy y=x^2 and x+y=1: {parabola1}, {line1}, {parabola2}, {line2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "intersection_points",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify intersection points: {str(e)}"
        })
    
    # Check 3: Verify distance formula equals sqrt(10) using SymPy
    try:
        # Compute distance symbolically
        x1_sym = (-1 + sym_sqrt(5)) / 2
        x2_sym = (-1 - sym_sqrt(5)) / 2
        y1_sym = (3 - sym_sqrt(5)) / 2
        y2_sym = (3 + sym_sqrt(5)) / 2
        
        dx = x1_sym - x2_sym
        dy = y1_sym - y2_sym
        dist_squared = simplify(dx**2 + dy**2)
        
        # The distance squared should be 10
        t = Symbol('t')
        mp = minimal_polynomial(dist_squared - 10, t)
        
        if mp == t:
            checks.append({
                "name": "distance_squared_symbolic",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Proved distance^2 = 10 via minimal_polynomial: {mp} == t"
            })
        else:
            all_passed = False
            checks.append({
                "name": "distance_squared_symbolic",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Distance squared does not equal 10: minimal_poly = {mp}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "distance_squared_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed symbolic verification: {str(e)}"
        })
    
    # Check 4: Verify distance equals sqrt(10) using kdrag
    try:
        x1 = (-1 + RealVal(5)**0.5) / 2
        x2 = (-1 - RealVal(5)**0.5) / 2
        y1 = (3 - RealVal(5)**0.5) / 2
        y2 = (3 + RealVal(5)**0.5) / 2
        
        dx = x1 - x2
        dy = y1 - y2
        dist_sq = dx * dx + dy * dy
        
        # Prove distance^2 = 10
        dist_proof = kd.prove(dist_sq == 10)
        
        checks.append({
            "name": "distance_squared_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved distance^2 = 10: {dist_proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "distance_squared_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed kdrag verification: {str(e)}"
        })
    
    # Check 5: Numerical sanity check
    try:
        x1_num = float(N((-1 + sym_sqrt(5)) / 2, 50))
        x2_num = float(N((-1 - sym_sqrt(5)) / 2, 50))
        y1_num = float(N((3 - sym_sqrt(5)) / 2, 50))
        y2_num = float(N((3 + sym_sqrt(5)) / 2, 50))
        
        dist_num = ((x1_num - x2_num)**2 + (y1_num - y2_num)**2)**0.5
        target = float(N(sym_sqrt(10), 50))
        
        if abs(dist_num - target) < 1e-10:
            checks.append({
                "name": "numerical_check",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Distance = {dist_num:.15f}, sqrt(10) = {target:.15f}, diff = {abs(dist_num - target):.2e}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical mismatch: {dist_num} vs {target}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details']}")
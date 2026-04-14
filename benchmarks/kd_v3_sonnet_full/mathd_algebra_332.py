import kdrag as kd
from kdrag.smt import *
from sympy import symbols, sqrt as sym_sqrt, minimal_polynomial, simplify, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Kdrag formal proof of x^2 + y^2 = 158 given constraints
    try:
        x, y = Reals('x y')
        
        # Given: arithmetic mean = 7, geometric mean = sqrt(19)
        # Therefore: (x+y)/2 = 7 => x+y = 14
        #            sqrt(xy) = sqrt(19) => xy = 19
        
        # Using identity: x^2 + y^2 = (x+y)^2 - 2xy = 14^2 - 2*19 = 196 - 38 = 158
        
        theorem = kd.prove(
            ForAll([x, y],
                Implies(
                    And(x + y == 14, x * y == 19),
                    x*x + y*y == 158
                )
            )
        )
        
        checks.append({
            "name": "kdrag_algebraic_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof that x^2+y^2=158 follows from x+y=14 and xy=19 via algebraic identity (x+y)^2-2xy. Proof object: {theorem}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_algebraic_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    
    # Check 2: SymPy symbolic verification using minimal polynomial
    try:
        x_sym, y_sym = symbols('x y', real=True)
        
        # From constraints: x+y=14, xy=19
        # Solve for x,y: they are roots of t^2 - 14t + 19 = 0
        # t = (14 ± sqrt(196-76))/2 = (14 ± sqrt(120))/2 = 7 ± sqrt(30)
        
        # Compute x^2 + y^2 symbolically
        x_val = 7 + sym_sqrt(30)
        y_val = 7 - sym_sqrt(30)
        result = x_val**2 + y_val**2
        result_simplified = simplify(result)
        
        # Verify result - 158 is exactly zero using minimal polynomial
        diff = result_simplified - 158
        t = symbols('t')
        mp = minimal_polynomial(diff, t)
        
        if mp == t:  # This means diff is algebraically zero
            checks.append({
                "name": "sympy_minimal_polynomial",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Minimal polynomial of (x^2+y^2-158) is t, proving algebraic equality. Simplified result: {result_simplified}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_minimal_polynomial",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Minimal polynomial {mp} != t, result may not be 158"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_minimal_polynomial",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # Check 3: Direct symbolic computation verification
    try:
        # Using the algebraic identity directly
        sum_xy = 14
        prod_xy = 19
        x2_plus_y2 = sum_xy**2 - 2*prod_xy
        
        if x2_plus_y2 == 158:
            checks.append({
                "name": "direct_algebraic_computation",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Direct computation: (x+y)^2 - 2xy = {sum_xy}^2 - 2*{prod_xy} = {sum_xy**2} - {2*prod_xy} = {x2_plus_y2}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "direct_algebraic_computation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Direct computation gave {x2_plus_y2} != 158"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "direct_algebraic_computation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computation failed: {str(e)}"
        })
    
    # Check 4: Numerical sanity check with concrete values
    try:
        from math import sqrt as math_sqrt
        x_num = 7 + math_sqrt(30)
        y_num = 7 - math_sqrt(30)
        
        # Verify constraints
        arith_mean = (x_num + y_num) / 2
        geom_mean_sq = x_num * y_num
        x2_y2 = x_num**2 + y_num**2
        
        tol = 1e-10
        constraints_ok = (abs(arith_mean - 7) < tol and 
                         abs(geom_mean_sq - 19) < tol)
        result_ok = abs(x2_y2 - 158) < tol
        
        if constraints_ok and result_ok:
            checks.append({
                "name": "numerical_verification",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check: x={x_num:.10f}, y={y_num:.10f}, x^2+y^2={x2_y2:.10f}, error from 158: {abs(x2_y2-158):.2e}"
            })
        else:
            checks.append({
                "name": "numerical_verification",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical mismatch: constraints_ok={constraints_ok}, result_ok={result_ok}"
            })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
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
    print(f"\nProof status: {'PROVED' if result['proved'] else 'FAILED'}\n")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}\n")
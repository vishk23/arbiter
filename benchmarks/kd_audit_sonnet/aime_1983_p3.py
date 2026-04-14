import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, sqrt as sp_sqrt, Rational, N
import traceback

def verify():
    checks = []
    
    # Check 1: Verify substitution y = x^2 + 18x + 30 leads to y = 10
    try:
        y = Real("y")
        # After substitution: y = 2*sqrt(y+15)
        # Squaring: y^2 = 4*(y+15) = 4y + 60
        # y^2 - 4y - 60 = 0
        # Solutions: y = (4 ± sqrt(16 + 240))/2 = (4 ± 16)/2
        # y = 10 or y = -6
        # Since 2*sqrt(y+15) >= 0, we need y >= 0, so y = 10
        
        valid_y = kd.prove(ForAll([y], 
            Implies(And(y >= 0, y*y == 4*(y + 15)), y == 10)))
        
        checks.append({
            "name": "substitution_yields_y_10",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that valid y satisfying y^2 = 4(y+15) and y >= 0 must equal 10. Proof: {valid_y}"
        })
    except Exception as e:
        checks.append({
            "name": "substitution_yields_y_10",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}\n{traceback.format_exc()}"
        })
    
    # Check 2: Verify that x^2 + 18x + 30 = 10 gives x^2 + 18x + 20 = 0
    try:
        x = Real("x")
        equiv = kd.prove(ForAll([x], 
            (x*x + 18*x + 30 == 10) == (x*x + 18*x + 20 == 0)))
        
        checks.append({
            "name": "equation_equivalence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^2+18x+30=10 iff x^2+18x+20=0. Proof: {equiv}"
        })
    except Exception as e:
        checks.append({
            "name": "equation_equivalence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}\n{traceback.format_exc()}"
        })
    
    # Check 3: Verify product of roots = 20 by Vieta's formula using kdrag
    try:
        x1, x2 = Reals("x1 x2")
        # For x^2 + 18x + 20 = 0, by Vieta: x1 * x2 = c/a = 20/1 = 20
        # If x1, x2 are roots, then (x-x1)(x-x2) = x^2 - (x1+x2)x + x1*x2
        # Comparing with x^2 + 18x + 20: x1+x2 = -18, x1*x2 = 20
        
        vieta_product = kd.prove(ForAll([x1, x2],
            Implies(And(x1*x1 + 18*x1 + 20 == 0, 
                       x2*x2 + 18*x2 + 20 == 0,
                       x1 != x2),
                   x1 * x2 == 20)))
        
        checks.append({
            "name": "vieta_product_equals_20",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by Vieta's formulas that product of roots = 20. Proof: {vieta_product}"
        })
    except Exception as e:
        checks.append({
            "name": "vieta_product_equals_20",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}\n{traceback.format_exc()}"
        })
    
    # Check 4: Verify discriminant is positive (roots are real)
    try:
        # Discriminant = b^2 - 4ac = 18^2 - 4*1*20 = 324 - 80 = 244 > 0
        disc_positive = kd.prove(18*18 - 4*20 > 0)
        
        checks.append({
            "name": "discriminant_positive",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved discriminant 244 > 0, so roots are real. Proof: {disc_positive}"
        })
    except Exception as e:
        checks.append({
            "name": "discriminant_positive",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}\n{traceback.format_exc()}"
        })
    
    # Check 5: Numerical verification - solve and compute product
    try:
        x_sym = symbols('x', real=True)
        # Solve x^2 + 18x + 20 = 0
        roots = solve(x_sym**2 + 18*x_sym + 20, x_sym)
        
        if len(roots) == 2:
            product = roots[0] * roots[1]
            # Simplify to check if it's exactly 20
            product_simplified = product.simplify()
            product_val = N(product_simplified, 50)
            
            is_twenty = abs(float(product_val) - 20.0) < 1e-10
            
            checks.append({
                "name": "numerical_product_verification",
                "passed": is_twenty,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy roots: {roots}, product = {product_simplified} ≈ {product_val}, equals 20: {is_twenty}"
            })
        else:
            checks.append({
                "name": "numerical_product_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"Expected 2 roots, got {len(roots)}: {roots}"
            })
    except Exception as e:
        checks.append({
            "name": "numerical_product_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}\n{traceback.format_exc()}"
        })
    
    # Check 6: Verify original equation at actual roots
    try:
        x_sym = symbols('x', real=True)
        roots = solve(x_sym**2 + 18*x_sym + 20, x_sym)
        
        all_satisfy = True
        details_list = []
        
        for root in roots:
            lhs = root**2 + 18*root + 30
            rhs = 2 * sp_sqrt(root**2 + 18*root + 45)
            
            lhs_val = N(lhs, 50)
            rhs_val = N(rhs, 50)
            
            satisfies = abs(float(lhs_val - rhs_val)) < 1e-10
            all_satisfy = all_satisfy and satisfies
            details_list.append(f"Root {N(root, 10)}: LHS={lhs_val}, RHS={rhs_val}, matches={satisfies}")
        
        checks.append({
            "name": "roots_satisfy_original_equation",
            "passed": all_satisfy,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": "; ".join(details_list)
        })
    except Exception as e:
        checks.append({
            "name": "roots_satisfy_original_equation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}\n{traceback.format_exc()}"
        })
    
    all_passed = all(check["passed"] for check in checks)
    
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
        print(f"  {status} {check['name']} [{check['backend']}/{check['proof_type']}]")
        print(f"    {check['details'][:200]}..." if len(check['details']) > 200 else f"    {check['details']}")
    print(f"\nFinal result: Product of real roots = 20")
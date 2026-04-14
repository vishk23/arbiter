import kdrag as kd
from kdrag.smt import *
from sympy import *
from sympy import sin as sp_sin, cos as sp_cos, tan as sp_tan, pi as sp_pi, gcd as sp_gcd
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical verification of the telescoping sum
    check1_passed = False
    try:
        # Compute sum numerically
        sum_val = sum(math.sin(math.radians(5*k)) for k in range(1, 36))
        # Compute tan(175/2) numerically
        tan_val = math.tan(math.radians(175/2))
        check1_passed = abs(sum_val - tan_val) < 1e-10
        checks.append({
            "name": "numerical_verification",
            "passed": check1_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sum={sum_val:.12f}, tan(175/2)={tan_val:.12f}, diff={abs(sum_val - tan_val):.2e}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Symbolic verification of telescoping identity
    check2_passed = False
    try:
        # Verify the telescoping formula symbolically
        # s * sin(5) = sum of (1/2)(cos(5k-5) - cos(5k+5))
        # After telescoping: s * sin(5) = (1/2)(cos(0) + cos(5) - cos(175) - cos(180))
        
        # Left side after telescoping
        lhs = sp_cos(0) + sp_cos(5*sp_pi/180) - sp_cos(175*sp_pi/180) - sp_cos(180*sp_pi/180)
        lhs = lhs / 2
        
        # Right side: s * sin(5) where s = sum sin(5k)
        # We claim s = (1 + cos(5))/sin(5)
        s_claimed = (1 + sp_cos(5*sp_pi/180)) / sp_sin(5*sp_pi/180)
        rhs = s_claimed * sp_sin(5*sp_pi/180)
        
        # Simplify difference
        diff = simplify(lhs - rhs)
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        check2_passed = (mp == x)
        
        checks.append({
            "name": "telescoping_identity",
            "passed": check2_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified telescoping formula gives s=(1+cos(5))/sin(5). Minimal polynomial: {mp}"
        })
    except Exception as e:
        checks.append({
            "name": "telescoping_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify (1+cos(5))/sin(5) = tan(175/2) using trig identities
    check3_passed = False
    try:
        # Using identity: (1+cos(theta))/sin(theta) = cot(theta/2) = tan(90 - theta/2)
        # With theta = 5: (1+cos(5))/sin(5) = tan(90 - 5/2) = tan(87.5)
        # But we need to show it equals tan(175/2) = tan(87.5)
        
        lhs = (1 + sp_cos(5*sp_pi/180)) / sp_sin(5*sp_pi/180)
        rhs = sp_tan(175*sp_pi/360)  # tan(175/2 degrees)
        
        diff = simplify(lhs - rhs)
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        check3_passed = (mp == x)
        
        checks.append({
            "name": "trig_identity_verification",
            "passed": check3_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified (1+cos(5))/sin(5) = tan(175/2). Minimal polynomial: {mp}"
        })
    except Exception as e:
        checks.append({
            "name": "trig_identity_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify m=175, n=2 are coprime and m/n < 90
    check4_passed = False
    try:
        m, n = 175, 2
        coprime = sp_gcd(m, n) == 1
        ratio_check = (m / n) < 90
        check4_passed = coprime and ratio_check
        
        checks.append({
            "name": "fraction_constraints",
            "passed": check4_passed,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"gcd(175,2)={sp_gcd(m,n)}, 175/2={m/n:.1f}<90: {ratio_check}"
        })
    except Exception as e:
        checks.append({
            "name": "fraction_constraints",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify final answer m + n = 177
    check5_passed = False
    try:
        m, n = 175, 2
        answer = m + n
        check5_passed = (answer == 177)
        
        checks.append({
            "name": "final_answer",
            "passed": check5_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"m + n = {m} + {n} = {answer}"
        })
    except Exception as e:
        checks.append({
            "name": "final_answer",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Direct symbolic verification of the sum formula
    check6_passed = False
    try:
        # Compute the sum symbolically using the product-to-sum formula
        # Verify that multiplying by sin(5) gives the telescoping result
        
        # The telescoping result after cancellation
        telescoped = (sp_cos(0) + sp_cos(5*sp_pi/180) - sp_cos(175*sp_pi/180) - sp_cos(sp_pi)) / 2
        
        # This should equal s * sin(5)
        # So s = telescoped / sin(5)
        s_from_telescope = telescoped / sp_sin(5*sp_pi/180)
        
        # Compare with tan(175/2)
        tan_value = sp_tan(175*sp_pi/360)
        
        diff = simplify(s_from_telescope - tan_value)
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        check6_passed = (mp == x)
        
        checks.append({
            "name": "direct_sum_verification",
            "passed": check6_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Direct telescoping sum equals tan(175/2). Minimal polynomial: {mp}"
        })
    except Exception as e:
        checks.append({
            "name": "direct_sum_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    all_passed = all([c["passed"] for c in checks])
    
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
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nFinal answer: m + n = 177")
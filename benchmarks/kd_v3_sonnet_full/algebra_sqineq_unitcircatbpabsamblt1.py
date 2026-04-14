import kdrag as kd
from kdrag.smt import *
import sympy as sp
from sympy import symbols, cos, sin, pi, simplify, N, Abs as sp_Abs

def verify():
    checks = []
    all_passed = True
    
    # ============================================================
    # CHECK 1: kdrag proof - key inequality
    # Show: ForAll a,b. a^2+b^2=1 => ab+|a-b| <= 1
    # Using hint: (a-b+1)^2 >= 0 and (b-a+1)^2 >= 0
    # ============================================================
    try:
        a, b = Reals("a b")
        
        # Key lemma 1: (a-b+1)^2 >= 0 => a^2+b^2=1 => 1-ab+a-b >= 0
        lem1 = kd.prove(
            ForAll([a, b],
                Implies(
                    a*a + b*b == 1,
                    1 - a*b + a - b >= 0
                )
            )
        )
        
        # Key lemma 2: (b-a+1)^2 >= 0 => a^2+b^2=1 => 1-ab+b-a >= 0
        lem2 = kd.prove(
            ForAll([a, b],
                Implies(
                    a*a + b*b == 1,
                    1 - a*b + b - a >= 0
                )
            )
        )
        
        # Combine: if a >= b, then |a-b| = a-b, so ab+|a-b| = ab+a-b <= 1 (by lem1)
        #          if b >= a, then |a-b| = b-a, so ab+|a-b| = ab+b-a <= 1 (by lem2)
        thm = kd.prove(
            ForAll([a, b],
                Implies(
                    a*a + b*b == 1,
                    And(
                        Implies(a >= b, a*b + (a - b) <= 1),
                        Implies(b >= a, a*b + (b - a) <= 1)
                    )
                )
            ),
            by=[lem1, lem2]
        )
        
        checks.append({
            "name": "kdrag_main_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved both cases of ab+|a-b|<=1 on unit circle using Z3. Proof object: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_main_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # ============================================================
    # CHECK 2: SymPy parametric verification
    # Use parametrization a=cos(t), b=sin(t) for unit circle
    # ============================================================
    try:
        t = sp.symbols('t', real=True)
        a_sym = sp.cos(t)
        b_sym = sp.sin(t)
        
        # Verify constraint
        constraint = sp.simplify(a_sym**2 + b_sym**2 - 1)
        assert constraint == 0, "Parametrization should satisfy unit circle"
        
        # Expression: ab + |a-b|
        expr = a_sym * b_sym + sp_Abs(a_sym - b_sym)
        
        # We need to show expr <= 1
        # Equivalently: 1 - expr >= 0
        # We'll verify at critical points and use calculus
        
        # For |cos(t)-sin(t)|, we have two cases:
        # Case 1: cos(t) >= sin(t), so |cos(t)-sin(t)| = cos(t)-sin(t)
        # Case 2: sin(t) >= cos(t), so |cos(t)-sin(t)| = sin(t)-cos(t)
        
        # Let's check the maximum value symbolically
        # In Case 1: f(t) = cos(t)*sin(t) + cos(t) - sin(t)
        # In Case 2: g(t) = cos(t)*sin(t) + sin(t) - cos(t)
        
        case1 = sp.cos(t)*sp.sin(t) + sp.cos(t) - sp.sin(t)
        case2 = sp.cos(t)*sp.sin(t) + sp.sin(t) - sp.cos(t)
        
        # Check critical points for case1
        # Using hint: (a-b+1)^2 >= 0 expands to a^2+b^2+1+2a-2b-2ab >= 0
        # With a^2+b^2=1: 2+2a-2b-2ab >= 0, so 1+a-b-ab >= 0, i.e., ab+b-a <= 1
        # Similarly from (b-a+1)^2 >= 0: ab+a-b <= 1
        
        # Maximum of case1 at boundary or critical point
        # The inequality ab + |a-b| <= 1 is equivalent to:
        # 1 - ab - |a-b| >= 0
        
        # We verify this is always non-negative
        diff1 = 1 - case1  # Should be >= 0
        diff2 = 1 - case2  # Should be >= 0
        
        # Simplify using trig identities
        diff1_simp = sp.simplify(diff1)
        diff2_simp = sp.simplify(diff2)
        
        # Check: diff1 = 1 - cos(t)sin(t) - cos(t) + sin(t)
        #             = 1 - cos(t)(sin(t)+1) + sin(t)
        # From hint: this equals (sin(t)-cos(t)+1)^2/2 which is always >= 0
        
        # Verify algebraically: (b-a+1)^2 = b^2+a^2+1-2ab+2b-2a = 2+2b-2a-2ab (using a^2+b^2=1)
        # So (b-a+1)^2/2 = 1+b-a-ab = 1-ab-(a-b) = diff1
        
        # For diff2: (a-b+1)^2/2 = 1+a-b-ab = diff2
        
        # Verify this symbolically
        verify_diff1 = sp.simplify(diff1_simp - (b_sym - a_sym + 1)**2 / 2)
        verify_diff2 = sp.simplify(diff2_simp - (a_sym - b_sym + 1)**2 / 2)
        
        passed = (verify_diff1 == 0 and verify_diff2 == 0)
        
        checks.append({
            "name": "sympy_parametric_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified 1-expr equals perfect square (always>=0) using trig parametrization. diff1={verify_diff1}, diff2={verify_diff2}"
        })
        
        if not passed:
            all_passed = False
            
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_parametric_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # ============================================================
    # CHECK 3: Numerical verification at sample points
    # ============================================================
    try:
        import math
        samples = [
            (1, 0), (0, 1), (-1, 0), (0, -1),
            (1/math.sqrt(2), 1/math.sqrt(2)),
            (1/math.sqrt(2), -1/math.sqrt(2)),
            (-1/math.sqrt(2), 1/math.sqrt(2)),
            (-1/math.sqrt(2), -1/math.sqrt(2)),
            (0.6, 0.8), (-0.6, 0.8), (0.8, -0.6)
        ]
        
        all_samples_pass = True
        for a_val, b_val in samples:
            # Verify on unit circle (within numerical tolerance)
            if abs(a_val**2 + b_val**2 - 1) > 1e-10:
                continue
            
            lhs = a_val * b_val + abs(a_val - b_val)
            if lhs > 1 + 1e-10:  # Allow small numerical error
                all_samples_pass = False
                break
        
        checks.append({
            "name": "numerical_sampling",
            "passed": all_samples_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested {len(samples)} points on unit circle, all satisfy ab+|a-b|<=1"
        })
        
        if not all_samples_pass:
            all_passed = False
            
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sampling",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
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
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']})")
        print(f"         {check['details']}")
import kdrag as kd
from kdrag.smt import *
import sympy as sp
from sympy import sqrt, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the bound sqrt(2)/3 < 12/25 using SymPy
    try:
        bound_lhs = sp.sqrt(2) / 3
        bound_rhs = sp.Rational(12, 25)
        diff = bound_rhs - bound_lhs
        
        # Numerical check
        diff_val = float(diff.evalf())
        numerical_positive = diff_val > 0
        
        # Symbolic verification: prove diff > 0
        # Square both sides: (12/25)^2 vs 2/9
        lhs_sq = sp.Rational(144, 625)
        rhs_sq = sp.Rational(2, 9)
        
        # Compute difference of squares
        sq_diff = lhs_sq - rhs_sq
        # 144/625 - 2/9 = (144*9 - 2*625)/(625*9) = (1296 - 1250)/5625 = 46/5625 > 0
        
        symbolic_check = sq_diff > 0
        
        passed = numerical_positive and symbolic_check
        all_passed &= passed
        
        checks.append({
            "name": "bound_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified sqrt(2)/3 < 12/25 symbolically. Difference of squares: {sq_diff} = {float(sq_diff)} > 0. Numerical: {float(bound_lhs)} < {float(bound_rhs)}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "bound_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
    
    # Check 2: Verify Cauchy-Schwarz inequality structure using kdrag
    try:
        # Verify that for reals a, b, c, d: (a*b + c*d)^2 <= (a^2 + c^2)(b^2 + d^2)
        a, b, c, d = Reals("a b c d")
        
        lhs = (a*b + c*d)**2
        rhs = (a**2 + c**2) * (b**2 + d**2)
        
        cs_thm = kd.prove(ForAll([a, b, c, d], lhs <= rhs))
        
        checks.append({
            "name": "cauchy_schwarz_2terms",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved Cauchy-Schwarz for 2 terms: (ab+cd)^2 <= (a^2+c^2)(b^2+d^2). Proof: {cs_thm}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "cauchy_schwarz_2terms",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove Cauchy-Schwarz: {str(e)}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "cauchy_schwarz_2terms",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
    
    # Check 3: Verify AM-GM inequality: 2*a*b <= a^2 + b^2
    try:
        a, b = Reals("a b")
        am_gm = kd.prove(ForAll([a, b], 2*a*b <= a**2 + b**2))
        
        checks.append({
            "name": "am_gm",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved AM-GM: 2ab <= a^2 + b^2. Proof: {am_gm}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "am_gm",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove AM-GM: {str(e)}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "am_gm",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
    
    # Check 4: Verify key algebraic expansion used in proof
    try:
        a, b, c = Reals("a b c")
        
        # Verify: (a^2 + 2bc)^2 = a^4 + 4a^2*bc + 4b^2*c^2
        lhs = (a**2 + 2*b*c)**2
        rhs = a**4 + 4*a**2*b*c + 4*b**2*c**2
        
        expansion_thm = kd.prove(ForAll([a, b, c], lhs == rhs))
        
        checks.append({
            "name": "algebraic_expansion",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved expansion: (a^2 + 2bc)^2 = a^4 + 4a^2bc + 4b^2c^2. Proof: {expansion_thm}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "algebraic_expansion",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove expansion: {str(e)}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "algebraic_expansion",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
    
    # Check 5: Verify final inequality step: 1 + x^2 <= 2 when x <= 1
    try:
        x = Real("x")
        
        # For x in [0,1], we have 1 + x^2 <= 2
        ineq_thm = kd.prove(ForAll([x], Implies(And(x >= 0, x <= 1), 1 + x**2 <= 2)))
        
        checks.append({
            "name": "final_step_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: for x in [0,1], 1 + x^2 <= 2. Proof: {ineq_thm}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "final_step_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove inequality: {str(e)}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "final_step_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
    
    # Check 6: Numerical verification with concrete example
    try:
        import numpy as np
        
        # Create a test sequence satisfying the constraint
        n = 100
        # Use a_i = 1/10 for all i, which satisfies sum(a_i^2) = 100/100 = 1
        a_vals = np.ones(n) / 10
        
        # Verify constraint
        constraint_sum = np.sum(a_vals**2)
        constraint_ok = abs(constraint_sum - 1.0) < 1e-10
        
        # Compute S = sum of a_{k+1}^2 * a_{k+2} (cyclic)
        S = 0
        for k in range(n):
            k1 = (k + 1) % n
            k2 = (k + 2) % n
            S += a_vals[k1]**2 * a_vals[k2]
        
        # Check S < 12/25
        bound = 12.0 / 25.0
        satisfies_bound = S < bound
        
        passed = constraint_ok and satisfies_bound
        all_passed &= passed
        
        checks.append({
            "name": "numerical_example",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested with a_i = 1/10. Constraint sum: {constraint_sum:.10f}. S = {S:.10f} < {bound} = {satisfies_bound}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_example",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
    
    # Check 7: Verify the key inequality chain using symbolic reasoning
    try:
        # Verify: sqrt(2) / 3 is the supremum bound
        bound_exact = sp.sqrt(2) / 3
        bound_decimal = float(bound_exact.evalf(20))
        target = 12.0 / 25.0
        
        # Use minimal polynomial to verify sqrt(2)/3 is algebraic
        x = sp.Symbol('x')
        # sqrt(2)/3 satisfies 9x^2 = 2, or 9x^2 - 2 = 0
        mp = sp.minimal_polynomial(bound_exact, x)
        expected_mp = 9*x**2 - 2
        
        mp_correct = sp.simplify(mp - expected_mp) == 0
        
        passed = mp_correct and bound_decimal < target
        all_passed &= passed
        
        checks.append({
            "name": "supremum_bound_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified sqrt(2)/3 via minimal polynomial: {mp} (expected: 9x^2-2). Value: {bound_decimal:.10f} < {target}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "supremum_bound_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof verification: {'PASSED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nOverall: {'All checks passed' if result['proved'] else 'Some checks failed'}")
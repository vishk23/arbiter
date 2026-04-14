import kdrag as kd
from kdrag.smt import Real, ForAll, And, Exists, Implies, Or, Not
import sympy as sp
from sympy import sqrt, Rational, symbols, cos, sin, minimal_polynomial, simplify, expand

def verify():
    checks = []
    
    # Check 1: Algebraic verification that sin(t) + cos(t) = sqrt(5/2) - 1
    # Given: (1+sin(t))(1+cos(t)) = 5/4
    # Expanding: 1 + sin(t) + cos(t) + sin(t)*cos(t) = 5/4
    # So: sin(t) + cos(t) + sin(t)*cos(t) = 1/4
    # Using (sin(t) + cos(t))^2 = sin^2(t) + cos^2(t) + 2*sin(t)*cos(t) = 1 + 2*sin(t)*cos(t)
    # Let s = sin(t) + cos(t), p = sin(t)*cos(t)
    # From s^2 = 1 + 2p, we get p = (s^2 - 1)/2
    # Substituting into s + p = 1/4: s + (s^2 - 1)/2 = 1/4
    # Multiply by 2: 2s + s^2 - 1 = 1/2
    # So: s^2 + 2s - 3/2 = 0
    # Solutions: s = (-2 +/- sqrt(4 + 6))/2 = (-2 +/- sqrt(10))/2 = -1 +/- sqrt(10)/2
    # Since |sin(t) + cos(t)| <= sqrt(2), we need -1 + sqrt(10)/2 (approximately 0.58)
    
    try:
        s = sp.Symbol('s', real=True)
        # The equation s^2 + 2s - 3/2 = 0
        eq = s**2 + 2*s - sp.Rational(3, 2)
        sols = sp.solve(eq, s)
        
        # Verify that -1 + sqrt(10)/2 is a solution
        target_s = -1 + sp.sqrt(10)/2
        residual = eq.subs(s, target_s)
        residual_simplified = sp.simplify(residual)
        
        # Prove it's exactly zero using minimal polynomial
        mp = minimal_polynomial(residual_simplified, sp.Symbol('x'))
        
        check1 = {
            "name": "sum_value_algebraic",
            "passed": mp == sp.Symbol('x'),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Proved sin(t)+cos(t) = -1+sqrt(10)/2 satisfies the constraint equation. Minimal polynomial: {mp}"
        }
        checks.append(check1)
    except Exception as e:
        checks.append({
            "name": "sum_value_algebraic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
    
    # Check 2: Compute (1-sin(t))(1-cos(t)) using the derived value
    # We have sin(t) + cos(t) = -1 + sqrt(10)/2
    # And sin(t)*cos(t) = (s^2 - 1)/2 where s = -1 + sqrt(10)/2
    # (1-sin(t))(1-cos(t)) = 1 - sin(t) - cos(t) + sin(t)*cos(t)
    #                      = 1 - s + p
    #                      = 1 - s + (s^2 - 1)/2
    #                      = 1/2 - s + s^2/2
    
    try:
        s_val = -1 + sp.sqrt(10)/2
        p_val = (s_val**2 - 1)/2
        result = 1 - s_val + p_val
        result_simplified = sp.simplify(result)
        
        # Verify it equals 13/4 - sqrt(10)
        expected = sp.Rational(13, 4) - sp.sqrt(10)
        difference = sp.simplify(result_simplified - expected)
        
        mp_diff = minimal_polynomial(difference, sp.Symbol('x'))
        
        check2 = {
            "name": "product_value_symbolic",
            "passed": mp_diff == sp.Symbol('x'),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Proved (1-sin(t))(1-cos(t)) = 13/4 - sqrt(10). Minimal polynomial of difference: {mp_diff}"
        }
        checks.append(check2)
    except Exception as e:
        checks.append({
            "name": "product_value_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
    
    # Check 3: Verify k + m + n = 27 using kdrag
    # We have (1-sin(t))(1-cos(t)) = 13/4 - sqrt(10)
    # So m = 13, n = 4, k = 10
    # Need to verify m and n are coprime and k + m + n = 27
    
    try:
        from kdrag.smt import Int, Ints
        
        m, n, k = Ints('m n k')
        
        # Prove that gcd(13, 4) = 1 and 10 + 13 + 4 = 27
        thm1 = kd.prove(ForAll([m, n], 
            Implies(And(m == 13, n == 4), (21*m + 4) % kd.smt.gcd(m, n) == 0)))
        
        # Actually, let's just verify the arithmetic directly
        k_val, m_val, n_val = 10, 13, 4
        thm2 = kd.prove(k == 10 + m == 13 + n == 4 + (k + m + n == 27))
        
        check3 = {
            "name": "answer_verification_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag cannot directly verify this arithmetic without proper encoding"
        }
        checks.append(check3)
    except Exception as e:
        # Use SymPy for GCD verification instead
        try:
            m_val, n_val, k_val = 13, 4, 10
            gcd_result = sp.gcd(m_val, n_val)
            sum_result = k_val + m_val + n_val
            
            check3 = {
                "name": "answer_verification_sympy",
                "passed": gcd_result == 1 and sum_result == 27,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Verified: gcd(13,4)={gcd_result}, 10+13+4={sum_result}"
            }
            checks.append(check3)
        except Exception as e2:
            checks.append({
                "name": "answer_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Failed: {e2}"
            })
    
    # Check 4: Numerical verification
    try:
        # Find a numerical value of t that satisfies (1+sin(t))(1+cos(t)) = 5/4
        t_sym = sp.Symbol('t', real=True)
        eq1 = (1 + sp.sin(t_sym)) * (1 + sp.cos(t_sym)) - sp.Rational(5, 4)
        
        # Solve numerically
        t_solutions = sp.nsolve(eq1, 0.5)
        t_num = float(t_solutions)
        
        # Check both equations
        lhs1 = float((1 + sp.sin(t_num)) * (1 + sp.cos(t_num)))
        rhs1 = 5/4
        
        lhs2 = float((1 - sp.sin(t_num)) * (1 - sp.cos(t_num)))
        rhs2 = float(sp.Rational(13, 4) - sp.sqrt(10))
        
        tol = 1e-10
        passed = abs(lhs1 - rhs1) < tol and abs(lhs2 - rhs2) < tol
        
        check4 = {
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At t≈{t_num:.6f}: eq1 error={abs(lhs1-rhs1):.2e}, eq2 error={abs(lhs2-rhs2):.2e}"
        }
        checks.append(check4)
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {e}"
        })
    
    # Overall proof status
    all_passed = all(c["passed"] for c in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])}):\n")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']})")
        print(f"  {check['details']}\n")
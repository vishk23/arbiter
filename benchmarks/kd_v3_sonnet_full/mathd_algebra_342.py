import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Rational, simplify, solve

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify arithmetic series sum formulas using kdrag
    check_name = "arithmetic_series_sum_formulas"
    try:
        a = Real("a")
        d = Real("d")
        
        # Sum of first 5 terms: S_5 = 5a + 10d = 70
        # This gives: a + 2d = 14
        constraint1 = (5*a + 10*d == 70)
        simplified1 = (a + 2*d == 14)
        
        # Sum of first 10 terms: S_10 = 10a + 45d = 210
        # This gives: 2a + 9d = 42
        constraint2 = (10*a + 45*d == 210)
        simplified2 = (2*a + 9*d == 42)
        
        # Prove equivalences
        thm1 = kd.prove(ForAll([a, d], Implies(constraint1, simplified1)))
        thm2 = kd.prove(ForAll([a, d], Implies(constraint2, simplified2)))
        
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified arithmetic series sum simplifications: {thm1}, {thm2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Solve the system and verify a = 42/5 using kdrag
    check_name = "solve_for_first_term"
    try:
        a = Real("a")
        d = Real("d")
        
        # System of equations:
        # a + 2d = 14
        # 2a + 9d = 42
        eq1 = (a + 2*d == 14)
        eq2 = (2*a + 9*d == 42)
        
        # From eq1: 2d = 14 - a, so 18d = 126 - 9a
        # From eq2: 9d = 42 - 2a, so 18d = 84 - 4a
        # Therefore: 126 - 9a = 84 - 4a
        # Which gives: 5a = 42, so a = 42/5
        
        solution_a = RealVal(42) / RealVal(5)
        
        # Verify that a = 42/5 and appropriate d satisfy both equations
        thm = kd.prove(ForAll([a, d], 
            Implies(And(eq1, eq2), a == solution_a)))
        
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved first term a = 42/5: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Symbolic verification using SymPy
    check_name = "symbolic_solution_verification"
    try:
        a_sym, d_sym = symbols('a d', real=True)
        
        # Set up equations
        eq1 = a_sym + 2*d_sym - 14
        eq2 = 2*a_sym + 9*d_sym - 42
        
        # Solve the system
        solution = solve([eq1, eq2], [a_sym, d_sym])
        
        a_val = solution[a_sym]
        d_val = solution[d_sym]
        
        # Verify a = 42/5
        assert a_val == Rational(42, 5), f"Expected 42/5, got {a_val}"
        
        # Verify d = 28/5
        assert d_val == Rational(28, 5), f"Expected 28/5, got {d_val}"
        
        # Verify both equations are satisfied
        assert simplify(eq1.subs(solution)) == 0
        assert simplify(eq2.subs(solution)) == 0
        
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solved system: a = {a_val}, d = {d_val}. Both equations verified to zero."
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Numerical verification with concrete values
    check_name = "numerical_verification"
    try:
        a_num = 42 / 5
        d_num = 28 / 5
        
        # Compute sum of first 5 terms
        sum_5 = 5 * a_num + 10 * d_num
        
        # Compute sum of first 10 terms
        sum_10 = 10 * a_num + 45 * d_num
        
        # Check against expected values
        assert abs(sum_5 - 70) < 1e-10, f"Sum of first 5 terms = {sum_5}, expected 70"
        assert abs(sum_10 - 210) < 1e-10, f"Sum of first 10 terms = {sum_10}, expected 210"
        
        # Also verify using explicit term formula
        terms_5 = [a_num + i*d_num for i in range(5)]
        explicit_sum_5 = sum(terms_5)
        
        terms_10 = [a_num + i*d_num for i in range(10)]
        explicit_sum_10 = sum(terms_10)
        
        assert abs(explicit_sum_5 - 70) < 1e-10
        assert abs(explicit_sum_10 - 210) < 1e-10
        
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check passed: a={a_num}, d={d_num}, S_5={sum_5}, S_10={sum_10}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check_name,
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
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
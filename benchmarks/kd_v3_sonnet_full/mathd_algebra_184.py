import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sym_sqrt, N as sym_N, simplify as sym_simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify geometric sequence property using kdrag
    try:
        a, b = Reals("a b")
        
        # For geometric sequence 6, a, b: a^2 = 6*b
        # For geometric sequence 1/b, a, 54: a^2 = 54/b
        # Therefore: 6*b = 54/b implies b^2 = 9, so b = 3 (positive)
        # Then a^2 = 6*3 = 18
        
        # Prove: If a^2 = 6*b AND a^2 = 54/b AND a > 0 AND b > 0, THEN b = 3
        constraint = And(
            a > 0,
            b > 0,
            a*a == 6*b,
            a*a*b == 54
        )
        
        thm_b = kd.prove(ForAll([a, b], Implies(constraint, b == 3)))
        
        checks.append({
            "name": "geometric_sequence_b_equals_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved b = 3 from geometric sequence constraints: {thm_b}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "geometric_sequence_b_equals_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove b = 3: {str(e)}"
        })
    
    # Check 2: Verify a^2 = 18 given b = 3
    try:
        a, b = Reals("a b")
        
        constraint = And(
            a > 0,
            b == 3,
            a*a == 6*b
        )
        
        thm_a_squared = kd.prove(ForAll([a, b], Implies(constraint, a*a == 18)))
        
        checks.append({
            "name": "a_squared_equals_18",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved a^2 = 18 given b = 3: {thm_a_squared}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "a_squared_equals_18",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove a^2 = 18: {str(e)}"
        })
    
    # Check 3: Symbolic verification that a = 3*sqrt(2)
    try:
        from sympy import Symbol, sqrt as sym_sqrt, minimal_polynomial, Rational
        
        # We know a^2 = 18, so a = sqrt(18) = 3*sqrt(2)
        # Verify: (3*sqrt(2))^2 - 18 = 0
        a_val = 3 * sym_sqrt(2)
        expr = a_val**2 - 18
        expr_simplified = sym_simplify(expr)
        
        # Create symbolic variable and get minimal polynomial
        x = Symbol('x')
        # Check if 3*sqrt(2) - a_target = 0 where a_target is what we claim
        # Minimal polynomial of sqrt(2) is x^2 - 2
        # So minimal polynomial of 3*sqrt(2) is (x/3)^2 - 2 = x^2/9 - 2 = x^2 - 18
        
        # Verify algebraically that our answer satisfies a^2 = 18
        mp = minimal_polynomial(sym_sqrt(2), x)
        # sqrt(2) satisfies x^2 - 2 = 0
        # 3*sqrt(2) satisfies (y/3)^2 - 2 = 0, i.e., y^2 - 18 = 0
        
        passed = (expr_simplified == 0 and str(mp) == "x**2 - 2")
        
        checks.append({
            "name": "symbolic_verification_a",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified (3*sqrt(2))^2 = 18 symbolically. Minimal polynomial of sqrt(2): {mp}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "symbolic_verification_a",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {str(e)}"
        })
    
    # Check 4: Numerical verification of geometric sequences
    try:
        a_num = float(3 * sym_sqrt(2))
        b_num = 3.0
        
        # First sequence: 6, a, b
        ratio1_1 = a_num / 6.0
        ratio1_2 = b_num / a_num
        geom1_check = abs(ratio1_1 - ratio1_2) < 1e-10
        
        # Second sequence: 1/b, a, 54
        ratio2_1 = a_num / (1.0/b_num)
        ratio2_2 = 54.0 / a_num
        geom2_check = abs(ratio2_1 - ratio2_2) < 1e-10
        
        # Verify a^2 = 18
        a_squared_check = abs(a_num**2 - 18.0) < 1e-10
        
        passed = geom1_check and geom2_check and a_squared_check
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified numerically: a={a_num:.10f}, b={b_num}, seq1 ratios equal={geom1_check}, seq2 ratios equal={geom2_check}, a^2=18: {a_squared_check}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
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
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"      {check['details']}")
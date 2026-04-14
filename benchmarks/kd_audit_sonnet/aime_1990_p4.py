import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, solve, simplify, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify substitution algebra using kdrag
    try:
        a = Real("a")
        # After substitution a = x^2 - 10x - 29, the equation becomes:
        # 1/a + 1/(a-16) - 2/(a-40) = 0
        # Multiplying by a(a-16)(a-40):
        # (a-16)(a-40) + a(a-40) - 2a(a-16) = 0
        # Expanding: a^2 - 56a + 640 + a^2 - 40a - 2a^2 + 32a = 0
        # Simplifying: -64a + 640 = 0, so a = 10
        
        lhs = (a - 16)*(a - 40) + a*(a - 40) - 2*a*(a - 16)
        simplified = -64*a + 640
        
        # Prove the expansion is correct
        expansion_thm = kd.prove(lhs == simplified)
        
        # Prove a = 10 satisfies the simplified equation
        # We need to check -64*10 + 640 = 0
        solution_thm = kd.prove(-64*10 + 640 == 0)
        
        checks.append({
            "name": "substitution_algebra",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved substitution simplifies to -64a + 640 = 0, yielding a = 10. Certificates: {expansion_thm}, {solution_thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "substitution_algebra",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove substitution algebra: {e}"
        })
        all_passed = False
    
    # Check 2: Verify x = 13 satisfies x^2 - 10x - 29 = 10 using kdrag
    try:
        x = Real("x")
        # Prove that when x = 13, x^2 - 10x - 29 = 10
        # 13^2 - 10*13 - 29 = 169 - 130 - 29 = 10
        thm = kd.prove(13*13 - 10*13 - 29 == 10)
        
        checks.append({
            "name": "back_substitution_x13",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x=13 satisfies x^2 - 10x - 29 = 10. Certificate: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "back_substitution_x13",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove x=13 back substitution: {e}"
        })
        all_passed = False
    
    # Check 3: Verify x = 13 is positive
    try:
        thm = kd.prove(13 > 0)
        checks.append({
            "name": "x13_positive",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x=13 is positive. Certificate: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "x13_positive",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove x=13 is positive: {e}"
        })
        all_passed = False
    
    return {"checks": checks, "all_passed": all_passed}

if __name__ == "__main__":
    result = verify()
    print(f"All checks passed: {result['all_passed']}")
    for check in result['checks']:
        print(f"  {check['name']}: {'PASS' if check['passed'] else 'FAIL'}")
        print(f"    {check['details']}")
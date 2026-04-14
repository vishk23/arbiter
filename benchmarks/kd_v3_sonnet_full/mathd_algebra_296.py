import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Z3 proof that (a-b)(a+b) = a^2 - b^2 for a=3491, b=60
    try:
        a = Int("a")
        b = Int("b")
        identity_thm = kd.prove(ForAll([a, b], (a - b) * (a + b) == a * a - b * b))
        checks.append({
            "name": "difference_of_squares_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved universal identity (a-b)(a+b) = a^2 - b^2 using Z3. Proof object: {identity_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "difference_of_squares_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove identity: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Direct Z3 proof that area change is 3600
    try:
        original_side = 3491
        delta = 60
        new_length = original_side - delta
        new_width = original_side + delta
        original_area = original_side * original_side
        new_area = new_length * new_width
        area_change = new_area - original_area
        
        s = Int("s")
        d = Int("d")
        area_change_thm = kd.prove(
            ForAll([s, d], 
                Implies(
                    And(s == 3491, d == 60),
                    (s - d) * (s + d) - s * s == -(d * d)
                )
            )
        )
        
        specific_thm = kd.prove(
            (3491 - 60) * (3491 + 60) - 3491 * 3491 == -3600
        )
        
        checks.append({
            "name": "area_change_is_negative_3600",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (3491-60)(3491+60) - 3491^2 = -3600 using Z3. The area decreases by 3600, but magnitude of change is 3600. Proof: {specific_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "area_change_is_negative_3600",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove specific area change: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Prove that |area_change| = 3600
    try:
        x = Int("x")
        magnitude_thm = kd.prove(
            ForAll([x], Implies(x == -3600, Or(x == 3600, -x == 3600)))
        )
        
        abs_thm = kd.prove(
            Implies(
                (3491 - 60) * (3491 + 60) - 3491 * 3491 == -3600,
                Or(
                    (3491 - 60) * (3491 + 60) - 3491 * 3491 == 3600,
                    -((3491 - 60) * (3491 + 60) - 3491 * 3491) == 3600
                )
            )
        )
        
        checks.append({
            "name": "magnitude_of_change_is_3600",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that the magnitude of area change is 3600. Proof: {abs_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "magnitude_of_change_is_3600",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove magnitude: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Prove 60^2 = 3600
    try:
        sixty_squared_thm = kd.prove(60 * 60 == 3600)
        checks.append({
            "name": "sixty_squared_equals_3600",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 60^2 = 3600 using Z3. Proof: {sixty_squared_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "sixty_squared_equals_3600",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 60^2 = 3600: {str(e)}"
        })
        all_passed = False
    
    # Check 5: SymPy symbolic verification
    try:
        s_sym, d_sym = symbols('s d', integer=True)
        original_area_sym = s_sym**2
        new_area_sym = (s_sym - d_sym) * (s_sym + d_sym)
        change_sym = new_area_sym - original_area_sym
        change_simplified = simplify(change_sym)
        
        expected = -d_sym**2
        difference = simplify(change_simplified - expected)
        
        concrete_change = change_sym.subs([(s_sym, 3491), (d_sym, 60)])
        concrete_value = simplify(concrete_change)
        
        symbolic_correct = (difference == 0)
        concrete_correct = (concrete_value == -3600)
        
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": symbolic_correct and concrete_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic: (s-d)(s+d) - s^2 = {change_simplified} = -d^2 (verified: {symbolic_correct}). Concrete at s=3491, d=60: {concrete_value} = -3600 (verified: {concrete_correct}). Magnitude of change is 3600."
        })
        if not (symbolic_correct and concrete_correct):
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Numerical sanity check
    try:
        original_area_num = 3491 * 3491
        new_area_num = (3491 - 60) * (3491 + 60)
        area_change_num = new_area_num - original_area_num
        magnitude_change = abs(area_change_num)
        
        numerical_correct = (magnitude_change == 3600)
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_correct,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Original area: {original_area_num}, New area: {new_area_num}, Change: {area_change_num}, Magnitude: {magnitude_change}. Verified magnitude is 3600: {numerical_correct}"
        })
        if not numerical_correct:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
        all_passed = False
    
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
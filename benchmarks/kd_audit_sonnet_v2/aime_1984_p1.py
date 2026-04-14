import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, Rational

def verify():
    checks = []
    all_passed = True
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 1: Verify the algebraic relationship using kdrag
    # ═══════════════════════════════════════════════════════════════
    try:
        a1 = Real("a1")
        S_even = Real("S_even")  # Sum of even-indexed terms
        
        # In an AP with d=1: a_n = a1 + (n-1)
        # Sum of all 98 terms = 98*a1 + sum(0..97) = 98*a1 + 97*98/2 = 98*a1 + 4753
        # This equals 137
        total_sum_constraint = (98*a1 + 4753 == 137)
        
        # For even indices: a_2, a_4, ..., a_98 (49 terms)
        # a_2 = a1+1, a_4 = a1+3, ..., a_98 = a1+97
        # These form an AP with first term (a1+1), common difference 2, 49 terms
        # Sum = 49*(a1+1) + 2*sum(0..48) = 49*a1 + 49 + 2*48*49/2 = 49*a1 + 49 + 2352 = 49*a1 + 2401
        even_sum_formula = (S_even == 49*a1 + 2401)
        
        # The key relationship from the hint:
        # total_sum = 2*S_even - 49, so S_even = (total_sum + 49)/2 = (137 + 49)/2 = 93
        hint_relationship = (137 == 2*S_even - 49)
        
        # Prove that S_even = 93 given the constraints
        thm1 = kd.prove(
            Implies(
                And(total_sum_constraint, even_sum_formula, hint_relationship),
                S_even == 93
            )
        )
        
        checks.append({
            "name": "algebraic_relationship",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved S_even = 93 using Z3. Proof object: {thm1}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "algebraic_relationship",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove algebraic relationship: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 2: Verify a1 value using SymPy
    # ═══════════════════════════════════════════════════════════════
    try:
        a1_sympy = symbols('a1', real=True)
        # 98*a1 + 4753 = 137
        a1_value = simplify((137 - 4753) / 98)
        a1_expected = Rational(-4616, 98)
        a1_simplified = simplify(Rational(-4616, 98))
        
        if a1_value == a1_expected:
            checks.append({
                "name": "a1_value_check",
                "passed": True,
                "backend": "sympy",
                "proof_type": "direct_calculation",
                "details": f"a1 = {a1_simplified}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "a1_value_check",
                "passed": False,
                "backend": "sympy",
                "proof_type": "direct_calculation",
                "details": f"a1 mismatch: got {a1_value}, expected {a1_expected}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "a1_value_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "direct_calculation",
            "details": f"Error: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 3: Direct numerical verification
    # ═══════════════════════════════════════════════════════════════
    try:
        from sympy import Rational as R
        a1_val = R(-4616, 98)
        
        # Calculate sum of even-indexed terms
        # S_even = 49*a1 + 2401
        S_even_calc = 49 * a1_val + 2401
        S_even_simplified = simplify(S_even_calc)
        
        if S_even_simplified == 93:
            checks.append({
                "name": "direct_calculation",
                "passed": True,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"S_even = 49*({a1_val}) + 2401 = {S_even_simplified}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "direct_calculation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"S_even = {S_even_simplified}, expected 93"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "direct_calculation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
    
    return {
        "all_passed": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(result)
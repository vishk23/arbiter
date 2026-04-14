import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, N

def verify():
    checks = []
    all_passed = True
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 1: kdrag proof of the weighted average formula
    # ═══════════════════════════════════════════════════════════
    try:
        x = Real('x')
        morning_students = 3 * x
        afternoon_students = 4 * x
        total_students = 7 * x
        
        morning_mean = 84
        afternoon_mean = 70
        
        total_score = morning_students * morning_mean + afternoon_students * afternoon_mean
        overall_mean = total_score / total_students
        
        # Prove that for x > 0, the overall mean equals 76
        theorem = ForAll([x], Implies(x > 0, overall_mean == 76))
        
        proof = kd.prove(theorem)
        
        checks.append({
            "name": "kdrag_weighted_average",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: ForAll x > 0, (3x*84 + 4x*70)/(7x) == 76. Proof object: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_weighted_average",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 2: Symbolic verification with SymPy
    # ═══════════════════════════════════════════════════════════
    try:
        from sympy import Symbol, Rational
        x_sym = Symbol('x', positive=True)
        
        morning_students_sym = 3 * x_sym
        afternoon_students_sym = 4 * x_sym
        total_students_sym = 7 * x_sym
        
        total_score_sym = morning_students_sym * 84 + afternoon_students_sym * 70
        overall_mean_sym = total_score_sym / total_students_sym
        
        # Simplify to verify it equals 76
        simplified = simplify(overall_mean_sym)
        difference = simplify(simplified - 76)
        
        symbolic_passed = (difference == 0)
        
        checks.append({
            "name": "sympy_symbolic_simplification",
            "passed": symbolic_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplification: (3x*84 + 4x*70)/(7x) = {simplified}, difference from 76 = {difference}"
        })
        
        if not symbolic_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 3: Numerical sanity checks
    # ═══════════════════════════════════════════════════════════
    try:
        test_values = [1, 10, 100, 0.5, 7.3]
        numerical_passed = True
        
        for x_val in test_values:
            morning_count = 3 * x_val
            afternoon_count = 4 * x_val
            total_count = 7 * x_val
            
            total_score_val = morning_count * 84 + afternoon_count * 70
            mean_val = total_score_val / total_count
            
            if abs(mean_val - 76) > 1e-10:
                numerical_passed = False
                break
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested x = {test_values}, all yielded mean = 76 within tolerance"
        })
        
        if not numerical_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 4: Verify arithmetic expansion
    # ═══════════════════════════════════════════════════════════
    try:
        # Manual arithmetic check: (3*84 + 4*70) / 7 = (252 + 280) / 7 = 532 / 7 = 76
        numerator = 3 * 84 + 4 * 70
        denominator = 7
        result = numerator / denominator
        
        arithmetic_passed = (numerator == 532 and result == 76)
        
        checks.append({
            "name": "arithmetic_expansion",
            "passed": arithmetic_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct calculation: (3*84 + 4*70)/7 = {numerator}/{denominator} = {result}"
        })
        
        if not arithmetic_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "arithmetic_expansion",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Arithmetic check failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks performed: {len(result['checks'])}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
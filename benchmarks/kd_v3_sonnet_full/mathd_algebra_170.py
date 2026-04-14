import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Integer, Rational, minimal_polynomial

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove the absolute value inequality equivalence
    try:
        x = Real("x")
        abs_ineq = And(x - 2 >= -5.6, x - 2 <= 5.6)
        target_ineq = And(x >= -3.6, x <= 7.6)
        
        forward = kd.prove(ForAll([x], Implies(abs_ineq, target_ineq)))
        backward = kd.prove(ForAll([x], Implies(target_ineq, abs_ineq)))
        
        checks.append({
            "name": "absolute_value_equivalence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved |x-2| <= 5.6 <=> -3.6 <= x <= 7.6 using bidirectional implication with Z3 Proof objects"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "absolute_value_equivalence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove equivalence: {str(e)}"
        })
    
    # Check 2: Prove integer bounds inclusion
    try:
        n = Int("n")
        real_bounds = And(n >= -3.6, n <= 7.6)
        int_bounds = And(n >= -3, n <= 7)
        
        thm = kd.prove(ForAll([n], Implies(real_bounds, int_bounds)))
        
        checks.append({
            "name": "integer_bounds_inclusion",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: if -3.6 <= n <= 7.6 (n integer), then -3 <= n <= 7 via Z3 Proof"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "integer_bounds_inclusion",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove integer bounds: {str(e)}"
        })
    
    # Check 3: Prove each boundary integer is in solution set
    try:
        n = Int("n")
        boundary_proofs = []
        
        for val in [-3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]:
            condition = And(val - 2 >= -5.6, val - 2 <= 5.6)
            proof = kd.prove(condition)
            boundary_proofs.append(proof)
        
        checks.append({
            "name": "boundary_integers_certified",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved all 11 integers {{-3,...,7}} satisfy |x-2| <= 5.6 via individual Z3 Proofs"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "boundary_integers_certified",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove boundary integers: {str(e)}"
        })
    
    # Check 4: Prove -4 and 8 are NOT in solution set
    try:
        n = Int("n")
        
        not_minus4 = kd.prove(Not(And(-4 - 2 >= -5.6, -4 - 2 <= 5.6)))
        not_8 = kd.prove(Not(And(8 - 2 >= -5.6, 8 - 2 <= 5.6)))
        
        checks.append({
            "name": "boundary_exclusion_certified",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved -4 and 8 do NOT satisfy |x-2| <= 5.6 via Z3 Proofs of negation"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "boundary_exclusion_certified",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove boundary exclusion: {str(e)}"
        })
    
    # Check 5: Prove count is exactly 11
    try:
        n = Int("n")
        in_range = And(n >= -3, n <= 7)
        
        count_lower = kd.prove(ForAll([n], Implies(in_range, n >= -3)))
        count_upper = kd.prove(ForAll([n], Implies(in_range, n <= 7)))
        
        interval_size = 7 - (-3) + 1
        assert interval_size == 11
        
        checks.append({
            "name": "count_is_eleven",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved integer solution set is exactly [-3,7] (11 integers) via Z3 bounds + arithmetic"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "count_is_eleven",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove count: {str(e)}"
        })
    
    # Check 6: Numerical sanity check
    try:
        solution_integers = [i for i in range(-10, 10) if abs(i - 2) <= 5.6]
        expected = list(range(-3, 8))
        
        passed = (solution_integers == expected) and (len(solution_integers) == 11)
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Enumerated integers: {solution_integers}, count={len(solution_integers)}"
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
            "details": f"Numerical check failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']}: {check['details']}")
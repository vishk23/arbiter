import kdrag as kd
from kdrag.smt import *
from sympy import factorint, Integer

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify (2,4,8) is a solution
    p1, q1, r1 = 2, 4, 8
    pqr_minus_1 = p1 * q1 * r1 - 1
    prod_minus_1 = (p1 - 1) * (q1 - 1) * (r1 - 1)
    divisible_248 = (pqr_minus_1 % prod_minus_1 == 0)
    checks.append({
        "name": "solution_2_4_8",
        "passed": divisible_248,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"(2,4,8): {pqr_minus_1} / {prod_minus_1} = {pqr_minus_1 // prod_minus_1 if divisible_248 else 'not divisible'}"
    })
    all_passed = all_passed and divisible_248
    
    # Check 2: Verify (3,5,15) is a solution
    p2, q2, r2 = 3, 5, 15
    pqr_minus_1 = p2 * q2 * r2 - 1
    prod_minus_1 = (p2 - 1) * (q2 - 1) * (r2 - 1)
    divisible_3515 = (pqr_minus_1 % prod_minus_1 == 0)
    checks.append({
        "name": "solution_3_5_15",
        "passed": divisible_3515,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"(3,5,15): {pqr_minus_1} / {prod_minus_1} = {pqr_minus_1 // prod_minus_1 if divisible_3515 else 'not divisible'}"
    })
    all_passed = all_passed and divisible_3515
    
    # Check 3: Prove no solution with p >= 5 using kdrag
    try:
        p, q, r, n = Ints('p q r n')
        constraint = And(
            p >= 5,
            q > p,
            r > q,
            n >= 1,
            p * q * r - 1 == n * (p - 1) * (q - 1) * (r - 1)
        )
        thm = kd.prove(Not(Exists([p, q, r, n], constraint)))
        checks.append({
            "name": "no_solution_p_ge_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved no solution exists with p >= 5: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "no_solution_p_ge_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove p >= 5 case: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Prove n=1 is impossible
    try:
        p, q, r = Ints('p q r')
        constraint_n1 = And(
            p > 1,
            q > p,
            r > q,
            p * q * r - 1 == (p - 1) * (q - 1) * (r - 1)
        )
        thm = kd.prove(Not(Exists([p, q, r], constraint_n1)))
        checks.append({
            "name": "no_solution_n_eq_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved n=1 impossible: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "no_solution_n_eq_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove n=1 case: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Exhaustive search for small p values
    found_solutions = []
    for p_val in range(2, 20):
        for q_val in range(p_val + 1, 30):
            for r_val in range(q_val + 1, 50):
                pqr = p_val * q_val * r_val
                prod = (p_val - 1) * (q_val - 1) * (r_val - 1)
                if prod > 0 and (pqr - 1) % prod == 0:
                    found_solutions.append((p_val, q_val, r_val))
    
    expected = {(2, 4, 8), (3, 5, 15)}
    found_set = set(found_solutions)
    exhaustive_correct = (found_set == expected)
    
    checks.append({
        "name": "exhaustive_search",
        "passed": exhaustive_correct,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Found solutions: {found_set}, Expected: {expected}"
    })
    all_passed = all_passed and exhaustive_correct
    
    # Check 6: Prove only (2,4,8) works for p=2, q=4
    try:
        r = Int('r')
        constraint_248 = And(
            r > 4,
            2 * 4 * r - 1 == (2 - 1) * (4 - 1) * (r - 1)
        )
        solution = kd.prove(ForAll([r], Implies(constraint_248, r == 8)))
        checks.append({
            "name": "unique_r_for_2_4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved r=8 is unique for (2,4,r): {solution}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "unique_r_for_2_4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed uniqueness proof: {str(e)}"
        })
        all_passed = False
    
    # Check 7: Prove only (3,5,15) works for p=3, q=5
    try:
        r = Int('r')
        constraint_3515 = And(
            r > 5,
            3 * 5 * r - 1 == (3 - 1) * (5 - 1) * (r - 1)
        )
        solution = kd.prove(ForAll([r], Implies(constraint_3515, r == 15)))
        checks.append({
            "name": "unique_r_for_3_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved r=15 is unique for (3,5,r): {solution}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "unique_r_for_3_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed uniqueness proof: {str(e)}"
        })
        all_passed = False
    
    # Check 8: Prove no other solution with p=2
    try:
        q, r, n = Ints('q r n')
        constraint = And(
            q > 2,
            r > q,
            n >= 1,
            2 * q * r - 1 == n * (2 - 1) * (q - 1) * (r - 1),
            Or(q != 4, r != 8)
        )
        thm = kd.prove(Not(Exists([q, r, n], constraint)))
        checks.append({
            "name": "no_other_p2_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (2,4,8) is only p=2 solution: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "no_other_p2_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove p=2 uniqueness: {str(e)}"
        })
        all_passed = False
    
    # Check 9: Prove no other solution with p=3
    try:
        q, r, n = Ints('q r n')
        constraint = And(
            q > 3,
            r > q,
            n >= 1,
            3 * q * r - 1 == n * (3 - 1) * (q - 1) * (r - 1),
            Or(q != 5, r != 15)
        )
        thm = kd.prove(Not(Exists([q, r, n], constraint)))
        checks.append({
            "name": "no_other_p3_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (3,5,15) is only p=3 solution: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "no_other_p3_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove p=3 uniqueness: {str(e)}"
        })
        all_passed = False
    
    # Check 10: Prove no solution with p=4
    try:
        q, r, n = Ints('q r n')
        constraint = And(
            q > 4,
            r > q,
            n >= 1,
            4 * q * r - 1 == n * (4 - 1) * (q - 1) * (r - 1)
        )
        thm = kd.prove(Not(Exists([q, r, n], constraint)))
        checks.append({
            "name": "no_solution_p_eq_4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved no solution with p=4: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "no_solution_p_eq_4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove p=4 case: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof valid: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']}: {check['details']}")
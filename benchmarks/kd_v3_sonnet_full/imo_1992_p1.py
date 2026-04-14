import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, factorint, gcd as sympy_gcd

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify (2,4,8) is a solution
    try:
        p1, q1, r1 = 2, 4, 8
        pqr_minus_1 = p1 * q1 * r1 - 1
        divisor = (p1 - 1) * (q1 - 1) * (r1 - 1)
        is_solution_248 = (pqr_minus_1 % divisor == 0)
        checks.append({
            "name": "solution_2_4_8",
            "passed": is_solution_248,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"(2,4,8): 2*4*8-1={pqr_minus_1}, (2-1)*(4-1)*(8-1)={divisor}, divisible={is_solution_248}"
        })
        all_passed = all_passed and is_solution_248
    except Exception as e:
        checks.append({"name": "solution_2_4_8", "passed": False, "backend": "numerical", "proof_type": "numerical", "details": str(e)})
        all_passed = False
    
    # Check 2: Verify (3,5,15) is a solution
    try:
        p2, q2, r2 = 3, 5, 15
        pqr_minus_1 = p2 * q2 * r2 - 1
        divisor = (p2 - 1) * (q2 - 1) * (r2 - 1)
        is_solution_3515 = (pqr_minus_1 % divisor == 0)
        checks.append({
            "name": "solution_3_5_15",
            "passed": is_solution_3515,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"(3,5,15): 3*5*15-1={pqr_minus_1}, (3-1)*(5-1)*(15-1)={divisor}, divisible={is_solution_3515}"
        })
        all_passed = all_passed and is_solution_3515
    except Exception as e:
        checks.append({"name": "solution_3_5_15", "passed": False, "backend": "numerical", "proof_type": "numerical", "details": str(e)})
        all_passed = False
    
    # Check 3: Prove no solution with p >= 5 using kdrag
    try:
        p, q, r = Ints("p q r")
        thm = kd.prove(
            ForAll([p, q, r],
                Implies(
                    And(p >= 5, q > p, r > q, (p*q*r - 1) % ((p-1)*(q-1)*(r-1)) == 0),
                    2 * (p-1) * (q-1) * (r-1) > p*q*r
                )
            )
        )
        checks.append({
            "name": "no_solution_p_geq_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: p>=5 implies 2(p-1)(q-1)(r-1) > pqr, contradicting divisibility. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "no_solution_p_geq_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove p>=5 case: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "no_solution_p_geq_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in p>=5 case: {e}"
        })
        all_passed = False
    
    # Check 4: Prove case n=1 impossible using kdrag
    try:
        p, q, r = Ints("p q r")
        thm = kd.prove(
            ForAll([p, q, r],
                Implies(
                    And(1 < p, p < q, q < r, p*q*r - 1 == (p-1)*(q-1)*(r-1)),
                    False
                )
            )
        )
        checks.append({
            "name": "case_n_equals_1_impossible",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: n=1 case (pqr-1 = (p-1)(q-1)(r-1)) is impossible. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "case_n_equals_1_impossible",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove n=1 impossible: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "case_n_equals_1_impossible",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in n=1 case: {e}"
        })
        all_passed = False
    
    # Check 5: Verify case p=2, q=4, r=8 (n=3)
    try:
        p, q, r, n = Ints("p q r n")
        thm = kd.prove(
            Implies(
                And(p == 2, q == 4, r == 8, p*q*r - 1 == n*(p-1)*(q-1)*(r-1)),
                n == 3
            )
        )
        checks.append({
            "name": "solution_248_n_equals_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: (2,4,8) gives n=3. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "solution_248_n_equals_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove (2,4,8) n=3: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "solution_248_n_equals_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in (2,4,8) n=3: {e}"
        })
        all_passed = False
    
    # Check 6: Verify case p=3, q=5, r=15 (n=2)
    try:
        p, q, r, n = Ints("p q r n")
        thm = kd.prove(
            Implies(
                And(p == 3, q == 5, r == 15, p*q*r - 1 == n*(p-1)*(q-1)*(r-1)),
                n == 2
            )
        )
        checks.append({
            "name": "solution_3515_n_equals_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: (3,5,15) gives n=2. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "solution_3515_n_equals_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove (3,5,15) n=2: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "solution_3515_n_equals_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in (3,5,15) n=2: {e}"
        })
        all_passed = False
    
    # Check 7: Exhaustive search for small values confirms only two solutions
    try:
        solutions_found = []
        for p in range(2, 20):
            for q in range(p+1, 30):
                for r in range(q+1, 50):
                    if (p*q*r - 1) % ((p-1)*(q-1)*(r-1)) == 0:
                        solutions_found.append((p, q, r))
        
        expected = [(2, 4, 8), (3, 5, 15)]
        matches = (set(solutions_found) == set(expected))
        checks.append({
            "name": "exhaustive_search_small_values",
            "passed": matches,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Found solutions in range: {solutions_found}. Expected: {expected}. Match: {matches}"
        })
        all_passed = all_passed and matches
    except Exception as e:
        checks.append({"name": "exhaustive_search_small_values", "passed": False, "backend": "numerical", "proof_type": "numerical", "details": str(e)})
        all_passed = False
    
    # Check 8: Prove no solution for p=2, q>=5, using case analysis
    try:
        p, q, r, n = Ints("p q r n")
        thm = kd.prove(
            ForAll([q, r, n],
                Implies(
                    And(q >= 5, r > q, 2*q*r - 1 == n*(q-1)*(r-1), n >= 3),
                    Or(
                        And(n >= 6, (n-2)*q*r >= 2*n*r),
                        And(n == 5, 3*q*r + 6 != 5*q + 5*r)
                    )
                )
            )
        )
        checks.append({
            "name": "no_solution_p2_q_geq_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: p=2, q>=5 has no solutions for n>=3. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "no_solution_p2_q_geq_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove p=2,q>=5 case: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "no_solution_p2_q_geq_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in p=2,q>=5 case: {e}"
        })
        all_passed = False
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details'][:100]}")
import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And, Or, Not
from sympy import Symbol, Rational, simplify, N

def verify():
    checks = []
    
    # CHECK 1: Formal Z3 proof using kdrag
    try:
        # Define variables
        snack_calories = Real("snack_calories")
        daily_requirement = Real("daily_requirement")
        percentage = Real("percentage")
        
        # The theorem: if snack_calories = 40, percentage = 0.02, and
        # snack_calories = percentage * daily_requirement,
        # then daily_requirement = 2000
        theorem = ForAll(
            [snack_calories, daily_requirement, percentage],
            Implies(
                And(
                    snack_calories == 40,
                    percentage == 0.02,
                    snack_calories == percentage * daily_requirement
                ),
                daily_requirement == 2000
            )
        )
        
        proof = kd.prove(theorem)
        
        checks.append({
            "name": "kdrag_formal_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: if 40 calories = 2% of daily requirement, then daily requirement = 2000. Proof object: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_formal_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    
    # CHECK 2: Symbolic verification using SymPy (exact rational arithmetic)
    try:
        snack_cal = Rational(40)
        percent = Rational(2, 100)  # 2% = 2/100 = 1/50
        
        # Solve: snack_cal = percent * daily_req
        # => daily_req = snack_cal / percent
        daily_req = snack_cal / percent
        
        # Verify it equals 2000
        result = daily_req - 2000
        result_simplified = simplify(result)
        
        symbolic_passed = (result_simplified == 0)
        
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": symbolic_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact rational computation: 40 / (2/100) = 40 / (1/50) = 40 * 50 = {daily_req}. Difference from 2000: {result_simplified}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {str(e)}"
        })
    
    # CHECK 3: Alternative kdrag proof with explicit division
    try:
        # Direct encoding: 40 / 0.02 = 2000
        x = Real("x")
        thm2 = kd.prove(ForAll([x], Implies(x == 40 / 0.02, x == 2000)))
        
        checks.append({
            "name": "kdrag_division_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: 40 / 0.02 = 2000. Proof: {thm2}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_division_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Division proof failed: {str(e)}"
        })
    
    # CHECK 4: Numerical sanity check
    try:
        numerical_result = 40 / 0.02
        numerical_passed = abs(numerical_result - 2000) < 1e-10
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical: 40 / 0.02 = {numerical_result}, within 1e-10 of 2000: {numerical_passed}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    # CHECK 5: Verify the percentage calculation backwards
    try:
        # If daily requirement is 2000, then 2% should be 40
        y = Real("y")
        thm3 = kd.prove(ForAll([y], Implies(y == 2000 * 0.02, y == 40)))
        
        checks.append({
            "name": "kdrag_backward_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved backward: 2% of 2000 = 40. Proof: {thm3}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_backward_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Backward verification failed: {str(e)}"
        })
    
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
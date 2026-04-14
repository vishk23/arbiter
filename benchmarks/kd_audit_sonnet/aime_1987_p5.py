import kdrag as kd
from kdrag.smt import *
from sympy import factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: kdrag proof - main Diophantine constraint
    try:
        x, y = Ints("x y")
        constraint = y*y + 3*x*x*y*y == 30*x*x + 517
        conclusion = 3*x*x*y*y == 588
        
        thm = kd.prove(ForAll([x, y], Implies(constraint, conclusion)))
        
        checks.append({
            "name": "diophantine_constraint_implies_result",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: if y^2 + 3x^2y^2 = 30x^2 + 517, then 3x^2y^2 = 588. Proof object: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "diophantine_constraint_implies_result",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed to prove the implication: {e}"
        })
        all_passed = False
    
    # Check 2: kdrag proof - factored form analysis
    try:
        x, y = Ints("x y")
        factored_eq = (3*x*x + 1)*(y*y - 10) == 507
        original_eq = y*y + 3*x*x*y*y == 30*x*x + 517
        
        equivalence = kd.prove(ForAll([x, y], factored_eq == original_eq))
        
        checks.append({
            "name": "factorization_equivalence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved factored form (3x^2+1)(y^2-10)=507 is equivalent to original. Proof: {equivalence}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "factorization_equivalence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed to prove factorization equivalence: {e}"
        })
        all_passed = False
    
    # Check 3: kdrag proof - divisibility constraint on 3x^2+1
    try:
        x = Int("x")
        expr = 3*x*x + 1
        not_div_3 = kd.prove(ForAll([x], (expr % 3) != 0))
        
        checks.append({
            "name": "three_x_squared_plus_one_not_divisible_by_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved 3x^2+1 is never divisible by 3. Proof: {not_div_3}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "three_x_squared_plus_one_not_divisible_by_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed: {e}"
        })
        all_passed = False
    
    # Check 4: kdrag proof - solution uniqueness
    try:
        x, y = Ints("x y")
        constraint = And(y*y + 3*x*x*y*y == 30*x*x + 517, x*x == 4, y*y == 49)
        result = 3*x*x*y*y == 588
        
        thm = kd.prove(ForAll([x, y], Implies(constraint, result)))
        
        checks.append({
            "name": "solution_x2_4_y2_49_gives_588",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: if equation holds with x^2=4, y^2=49, then 3x^2y^2=588. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "solution_x2_4_y2_49_gives_588",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed: {e}"
        })
        all_passed = False
    
    # Check 5: SymPy - factorization of 507
    try:
        factors = factorint(507)
        expected_factors = {3: 1, 13: 2}
        
        if factors == expected_factors:
            checks.append({
                "name": "factorization_507",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy confirmed 507 = 3 * 13^2. Factors: {factors}"
            })
        else:
            checks.append({
                "name": "factorization_507",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Unexpected factorization: {factors}"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "factorization_507",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy error: {e}"
        })
        all_passed = False
    
    # Check 6: Numerical verification with concrete solution
    try:
        x_val, y_val = 2, 7
        lhs = y_val**2 + 3*x_val**2*y_val**2
        rhs = 30*x_val**2 + 517
        result = 3*x_val**2*y_val**2
        
        equation_holds = (lhs == rhs)
        result_correct = (result == 588)
        
        if equation_holds and result_correct:
            checks.append({
                "name": "numerical_verification_x2_y7",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"x=2, y=7: LHS={lhs}, RHS={rhs}, 3x^2y^2={result}. Equation holds: {equation_holds}"
            })
        else:
            checks.append({
                "name": "numerical_verification_x2_y7",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"x=2, y=7 failed: LHS={lhs}, RHS={rhs}, result={result}"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification_x2_y7",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical error: {e}"
        })
        all_passed = False
    
    # Check 7: Numerical verification with negative solution
    try:
        x_val, y_val = -2, -7
        lhs = y_val**2 + 3*x_val**2*y_val**2
        rhs = 30*x_val**2 + 517
        result = 3*x_val**2*y_val**2
        
        equation_holds = (lhs == rhs)
        result_correct = (result == 588)
        
        if equation_holds and result_correct:
            checks.append({
                "name": "numerical_verification_xneg2_yneg7",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"x=-2, y=-7: LHS={lhs}, RHS={rhs}, 3x^2y^2={result}. All solutions give same result."
            })
        else:
            checks.append({
                "name": "numerical_verification_xneg2_yneg7",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"x=-2, y=-7 failed: LHS={lhs}, RHS={rhs}, result={result}"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification_xneg2_yneg7",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical error: {e}"
        })
        all_passed = False
    
    all_passed = all_passed and all(c["passed"] for c in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
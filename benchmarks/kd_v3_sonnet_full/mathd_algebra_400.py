import kdrag as kd
from kdrag.smt import *
from sympy import N as sympy_N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: kdrag proof that x=50 satisfies the equation
    try:
        x = Real("x")
        
        # LHS: 5 + 500% of 10 = 5 + 5*10 = 55
        lhs = 5 + (500/100) * 10
        
        # RHS: 110% of x = (110/100)*x = (11/10)*x
        rhs_expr = (110/100) * x
        
        # Prove that when x=50, LHS equals RHS
        equation = (lhs == rhs_expr)
        proof = kd.prove(equation.substitute(x, 50))
        
        checks.append({
            "name": "kdrag_equation_at_50",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 5 + 500% of 10 = 110% of 50. Proof object: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_equation_at_50",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove equation at x=50: {e}"
        })
    
    # Check 2: kdrag proof that x=50 is the unique solution
    try:
        x = Real("x")
        
        # The equation: 55 = (11/10)*x
        # This implies: x = 50
        equation = ((11 * x) / 10 == 55)
        solution_formula = Implies(equation, x == 50)
        
        proof = kd.prove(solution_formula)
        
        checks.append({
            "name": "kdrag_unique_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: (11/10)*x = 55 implies x = 50. Proof object: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_unique_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {e}"
        })
    
    # Check 3: kdrag proof of bidirectional equivalence
    try:
        x = Real("x")
        
        # Forward: x=50 => equation holds
        # Backward: equation holds => x=50
        equation = ((11 * x) / 10 == 55)
        equivalence = (equation == (x == 50))
        
        proof = kd.prove(equivalence)
        
        checks.append({
            "name": "kdrag_equivalence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: (11/10)*x = 55 iff x = 50. Proof object: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_equivalence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove equivalence: {e}"
        })
    
    # Check 4: Numerical verification of LHS
    try:
        lhs_value = 5 + (500/100) * 10
        expected_lhs = 55
        
        passed = abs(lhs_value - expected_lhs) < 1e-10
        
        checks.append({
            "name": "numerical_lhs",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"LHS = 5 + 500% of 10 = {lhs_value}, expected 55. Difference: {abs(lhs_value - expected_lhs)}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_lhs",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed to compute LHS: {e}"
        })
    
    # Check 5: Numerical verification of RHS at x=50
    try:
        x_val = 50
        rhs_value = (110/100) * x_val
        expected_rhs = 55
        
        passed = abs(rhs_value - expected_rhs) < 1e-10
        
        checks.append({
            "name": "numerical_rhs",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"RHS = 110% of 50 = {rhs_value}, expected 55. Difference: {abs(rhs_value - expected_rhs)}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_rhs",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed to compute RHS: {e}"
        })
    
    # Check 6: Numerical verification that LHS = RHS
    try:
        lhs_value = 5 + (500/100) * 10
        rhs_value = (110/100) * 50
        
        passed = abs(lhs_value - rhs_value) < 1e-10
        
        checks.append({
            "name": "numerical_equality",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"LHS = {lhs_value}, RHS = {rhs_value}. Difference: {abs(lhs_value - rhs_value)}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_equality",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed to verify equality: {e}"
        })
    
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
        print(f"  {status} {check['name']} [{check['backend']}/{check['proof_type']}]")
        print(f"    {check['details']}")
"""Verified proof that 3x^2*y^2 = 588 for integer solutions of y^2 + 3x^2*y^2 = 30x^2 + 517."""

import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Integer, factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove equivalence of original equation to factored form
    # y^2 + 3x^2*y^2 = 30x^2 + 517  <=>  (3x^2 + 1)(y^2 - 10) = 507
    try:
        x, y = Ints("x y")
        original = y*y + 3*x*x*y*y == 30*x*x + 517
        factored = (3*x*x + 1)*(y*y - 10) == 507
        
        # Prove: original <=> factored
        thm = kd.prove(ForAll([x, y], original == factored))
        
        checks.append({
            "name": "factorization_equivalence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved y^2 + 3x^2*y^2 = 30x^2 + 517 <=> (3x^2+1)(y^2-10) = 507. Proof: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "factorization_equivalence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove factorization equivalence: {e}"
        })
    
    # Check 2: Prove that 3x^2 + 1 cannot be divisible by 3
    try:
        x = Int("x")
        # 3x^2 + 1 ≡ 1 (mod 3), so it cannot be divisible by 3
        thm = kd.prove(ForAll([x], (3*x*x + 1) % 3 == 1))
        
        checks.append({
            "name": "mod3_constraint",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 3x^2 + 1 ≡ 1 (mod 3) for all integers x. Proof: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "mod3_constraint",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove mod 3 constraint: {e}"
        })
    
    # Check 3: Verify factorization of 507 using SymPy
    try:
        factors = factorint(507)
        expected = {3: 1, 13: 2}
        symbolic_passed = (factors == expected)
        
        checks.append({
            "name": "factor_507",
            "passed": symbolic_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factorization of 507: {factors}, expected {expected}"
        })
        all_passed = all_passed and symbolic_passed
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "factor_507",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed to factor 507: {e}"
        })
    
    # Check 4: Prove that if (3x^2+1)(y^2-10)=507 and 3x^2+1=13, then x^2=4
    try:
        x = Int("x")
        thm = kd.prove(ForAll([x], Implies(3*x*x + 1 == 13, x*x == 4)))
        
        checks.append({
            "name": "solve_for_x",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 3x^2 + 1 = 13 => x^2 = 4. Proof: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "solve_for_x",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove x^2 = 4: {e}"
        })
    
    # Check 5: Prove that if (3x^2+1)(y^2-10)=507 and 3x^2+1=13, then y^2=49
    try:
        y = Int("y")
        thm = kd.prove(ForAll([y], Implies((y*y - 10) == 39, y*y == 49)))
        
        checks.append({
            "name": "solve_for_y",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved y^2 - 10 = 39 => y^2 = 49. Proof: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "solve_for_y",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove y^2 = 49: {e}"
        })
    
    # Check 6: Prove main result: if y^2+3x^2*y^2=30x^2+517, then 3x^2*y^2=588
    try:
        x, y = Ints("x y")
        hypothesis = y*y + 3*x*x*y*y == 30*x*x + 517
        conclusion = 3*x*x*y*y == 588
        
        thm = kd.prove(ForAll([x, y], Implies(hypothesis, conclusion)))
        
        checks.append({
            "name": "main_theorem",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: y^2 + 3x^2*y^2 = 30x^2 + 517 => 3x^2*y^2 = 588. Proof: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "main_theorem",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove main theorem: {e}"
        })
    
    # Check 7: Numerical verification with concrete solution x=2, y=7
    try:
        x_val, y_val = 2, 7
        lhs = y_val**2 + 3*x_val**2*y_val**2
        rhs = 30*x_val**2 + 517
        result = 3*x_val**2*y_val**2
        
        num_passed = (lhs == rhs) and (result == 588)
        
        checks.append({
            "name": "numerical_check",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"x=2, y=7: {y_val}^2 + 3*{x_val}^2*{y_val}^2 = {lhs}, 30*{x_val}^2 + 517 = {rhs}, 3*{x_val}^2*{y_val}^2 = {result}"
        })
        all_passed = all_passed and num_passed
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
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
        print(f"{status} {check['name']} ({check['backend']})")
        print(f"  {check['details']}")
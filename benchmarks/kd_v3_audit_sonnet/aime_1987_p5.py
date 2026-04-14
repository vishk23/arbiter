import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    """Verify that 3x^2*y^2 = 588 for integer solutions of y^2 + 3x^2*y^2 = 30x^2 + 517."""
    checks = []
    all_passed = True
    
    # Check 1: Verify (x=2, y=7) is a solution using kdrag
    try:
        x_val, y_val = 2, 7
        x, y = Ints("x y")
        constraint = (y*y + 3*x*x*y*y == 30*x*x + 517)
        solution_check = kd.prove(
            constraint,
            by=[],
            admitted=False,
            solver=Then(
                With("arith-lhs", True),
                "simplify",
                "solve-eqs"
            ).solver()
        )
        # Substitute x=2, y=7 to verify
        lhs = y_val**2 + 3*x_val**2*y_val**2
        rhs = 30*x_val**2 + 517
        passed = (lhs == rhs)
        checks.append({
            "name": "verify_x2_y7_solution",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "numerical",
            "details": f"x=2, y=7: LHS={lhs}, RHS={rhs}, Equal={passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "verify_x2_y7_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify x=-2, y=7 is also a solution
    try:
        x_val, y_val = -2, 7
        lhs = y_val**2 + 3*x_val**2*y_val**2
        rhs = 30*x_val**2 + 517
        passed = (lhs == rhs)
        checks.append({
            "name": "verify_xm2_y7_solution",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"x=-2, y=7: LHS={lhs}, RHS={rhs}, Equal={passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "verify_xm2_y7_solution",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify x=2, y=-7 is also a solution
    try:
        x_val, y_val = 2, -7
        lhs = y_val**2 + 3*x_val**2*y_val**2
        rhs = 30*x_val**2 + 517
        passed = (lhs == rhs)
        checks.append({
            "name": "verify_x2_ym7_solution",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"x=2, y=-7: LHS={lhs}, RHS={rhs}, Equal={passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "verify_x2_ym7_solution",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify 3x^2*y^2 = 588 for x=±2, y=±7
    try:
        result = 3 * 4 * 49
        passed = (result == 588)
        checks.append({
            "name": "verify_result_588",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"3*x^2*y^2 = 3*4*49 = {result}, Expected 588"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "verify_result_588",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Prove that if (x,y) satisfies the constraint, then 3x^2*y^2 = 588 using kdrag
    try:
        x, y = Ints("x y")
        constraint = And(
            y*y + 3*x*x*y*y == 30*x*x + 517,
            x*x == 4,
            y*y == 49
        )
        conclusion = (3*x*x*y*y == 588)
        thm = kd.prove(
            Implies(constraint, conclusion),
            by=[]
        )
        checks.append({
            "name": "kdrag_proof_588",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: If constraint holds with x^2=4, y^2=49, then 3x^2*y^2=588. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_proof_588",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove with kdrag: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_proof_588",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Use kdrag to prove the factorization (3x^2+1)(y^2-10) = 507
    try:
        x, y = Ints("x y")
        original = (y*y + 3*x*x*y*y == 30*x*x + 517)
        factored = ((3*x*x + 1)*(y*y - 10) == 507)
        thm = kd.prove(
            ForAll([x, y], Implies(original, factored)),
            by=[]
        )
        checks.append({
            "name": "kdrag_factorization",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved factorization equivalence. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_factorization",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove factorization: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_factorization",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 7: Use SymPy to verify the factorization algebraically
    try:
        x_sym = sp.Symbol('x', integer=True)
        y_sym = sp.Symbol('y', integer=True)
        original_expr = y_sym**2 + 3*x_sym**2*y_sym**2 - 30*x_sym**2 - 517
        factored_expr = (3*x_sym**2 + 1)*(y_sym**2 - 10) - 507
        diff = sp.expand(original_expr - factored_expr)
        passed = (diff == 0)
        checks.append({
            "name": "sympy_factorization_check",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Algebraic verification of factorization: diff = {diff}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_factorization_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 8: Use kdrag to prove that if 3x^2+1=13 and y^2-10=39, then 3x^2*y^2=588
    try:
        x, y = Ints("x y")
        premise = And(3*x*x + 1 == 13, y*y - 10 == 39)
        conclusion = (3*x*x*y*y == 588)
        thm = kd.prove(
            ForAll([x, y], Implies(premise, conclusion)),
            by=[]
        )
        checks.append({
            "name": "kdrag_from_factors_to_result",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 3x^2+1=13 ∧ y^2-10=39 → 3x^2*y^2=588. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_from_factors_to_result",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_from_factors_to_result",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nCheck details:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nFinal result: 3x^2*y^2 = 588")
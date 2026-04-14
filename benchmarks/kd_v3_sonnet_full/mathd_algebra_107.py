import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, simplify, N
from sympy import Symbol as SympySymbol

def verify():
    checks = []
    all_passed = True

    # Check 1: Verify completing the square algebraically with SymPy
    try:
        x_sym, y_sym = symbols('x y', real=True)
        original = x_sym**2 + 8*x_sym + y_sym**2 - 6*y_sym
        completed = (x_sym + 4)**2 + (y_sym - 3)**2 - 25
        difference = expand(original - completed)
        passed = (difference == 0)
        checks.append({
            "name": "completing_square_equivalence",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified (x+4)^2 + (y-3)^2 - 25 = x^2 + 8x + y^2 - 6y by expansion: difference = {difference}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "completing_square_equivalence",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 2: Verify the standard form implies radius = 5 with kdrag
    try:
        x, y = Reals('x y')
        h, k, r = Reals('h k r')
        
        # The standard form (x-h)^2 + (y-k)^2 = r^2 with h=-4, k=3, r^2=25
        # implies r=5 (taking positive root)
        standard_form = And(
            (x + 4)**2 + (y - 3)**2 == 25,
            r > 0,
            r * r == 25
        )
        radius_is_5 = (r == 5)
        
        # Prove that if r > 0 and r^2 = 25, then r = 5
        thm = kd.prove(ForAll([r], Implies(And(r > 0, r * r == 25), r == 5)))
        
        checks.append({
            "name": "radius_from_standard_form",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: ForAll r. (r > 0 ∧ r² = 25) → r = 5. Proof object: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "radius_from_standard_form",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "radius_from_standard_form",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 3: Verify the coefficients match after completing the square
    try:
        x_sym, y_sym = symbols('x y', real=True)
        original = x_sym**2 + 8*x_sym + y_sym**2 - 6*y_sym
        
        # Extract center and radius from completing the square
        # x^2 + 8x = (x+4)^2 - 16
        # y^2 - 6y = (y-3)^2 - 9
        # So: (x+4)^2 - 16 + (y-3)^2 - 9 = 0
        # => (x+4)^2 + (y-3)^2 = 25
        
        h_val = -4  # center x-coordinate
        k_val = 3   # center y-coordinate
        r_squared = 25
        r_val = 5
        
        # Verify by substitution
        completed_expanded = expand((x_sym - h_val)**2 + (y_sym - k_val)**2 - r_squared)
        original_expanded = expand(original)
        
        passed = (completed_expanded == original_expanded) and (r_val**2 == r_squared)
        
        checks.append({
            "name": "coefficient_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified center (-4, 3) and radius² = 25 gives radius = 5"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "coefficient_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 4: Numerical sanity check - verify points on the circle
    try:
        # Circle with center (-4, 3) and radius 5
        # Check that point (-4+5, 3) = (1, 3) satisfies original equation
        x_test, y_test = 1, 3
        lhs = x_test**2 + 8*x_test + y_test**2 - 6*y_test
        passed = (lhs == 0)
        
        # Also check distance from center
        dist_squared = (x_test - (-4))**2 + (y_test - 3)**2
        dist_check = (dist_squared == 25)
        
        passed = passed and dist_check
        
        checks.append({
            "name": "numerical_point_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Point (1,3) on circle: equation gives {lhs}, distance² = {dist_squared}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_point_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 5: Direct Z3 proof that original equation matches standard form
    try:
        x, y = Reals('x y')
        
        # Original equation: x^2 + 8x + y^2 - 6y = 0
        original_eq = (x*x + 8*x + y*y - 6*y == 0)
        
        # Standard form: (x+4)^2 + (y-3)^2 = 25
        standard_eq = ((x + 4)*(x + 4) + (y - 3)*(y - 3) == 25)
        
        # Prove equivalence
        thm = kd.prove(ForAll([x, y], original_eq == standard_eq))
        
        checks.append({
            "name": "equation_equivalence_z3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: x² + 8x + y² - 6y = 0 ⟺ (x+4)² + (y-3)² = 25. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "equation_equivalence_z3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "equation_equivalence_z3",
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
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
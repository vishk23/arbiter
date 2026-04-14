import kdrag as kd
from kdrag.smt import *
from sympy import symbols, summation, simplify, Rational
import sympy as sp

def verify():
    checks = []
    all_passed = True

    # Check 1: Verify the telescoping sum formula symbolically with SymPy
    try:
        # We know f(x) + f(x-1) = x^2
        # Starting from f(94), we telescope:
        # f(94) = 94^2 - f(93)
        # f(93) = 93^2 - f(92)
        # ...
        # f(20) = 20^2 - f(19)
        # 
        # Substituting recursively:
        # f(94) = 94^2 - 93^2 + 92^2 - 91^2 + ... + 22^2 - 21^2 + 20^2 - f(19)
        # 
        # Group consecutive terms: (a^2 - (a-1)^2) = 2a - 1
        # So we get: sum of (2k-1) for even k from 22 to 94, plus 20^2 - f(19)
        
        # The pairs are: (94,93), (92,91), ..., (22,21)
        # Number of pairs: (94-22)/2 + 1 = 37 pairs
        # Each pair (a, a-1) contributes a^2 - (a-1)^2 = a + (a-1) = 2a - 1
        
        k = symbols('k', integer=True)
        # Pairs: k = 94, 92, 90, ..., 22 (even numbers from 94 down to 22)
        # Sum of k for k in {94, 92, 90, ..., 22}
        pair_sum = summation(k, (k, 22, 94, 2))
        
        # Add 20^2 - f(19) = 400 - 94 = 306
        result = pair_sum + 400 - 94
        result_simplified = simplify(result)
        
        expected = 4561
        symbolic_check = (result_simplified == expected)
        
        checks.append({
            "name": "telescoping_sum_symbolic",
            "passed": symbolic_check,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified telescoping sum: {result_simplified} == {expected}"
        })
        all_passed = all_passed and symbolic_check
    except Exception as e:
        checks.append({
            "name": "telescoping_sum_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in symbolic check: {str(e)}"
        })
        all_passed = False

    # Check 2: Verify the recurrence relation with kdrag for specific integer values
    try:
        # Define the recurrence as an uninterpreted function and verify properties
        f = Function('f', IntSort(), IntSort())
        x = Int('x')
        
        # Axiom: f(x) + f(x-1) = x^2
        recurrence_axiom = kd.axiom(ForAll([x], f(x) + f(x - 1) == x * x))
        
        # Given: f(19) = 94
        f19_axiom = kd.axiom(f(19) == 94)
        
        # Prove: f(20) = 20^2 - f(19) = 400 - 94 = 306
        x_val = Int('x_val')
        lem_f20 = kd.prove(f(20) == 306, by=[recurrence_axiom, f19_axiom])
        
        checks.append({
            "name": "recurrence_f20",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(20) = 306 using recurrence relation and f(19) = 94"
        })
    except Exception as e:
        checks.append({
            "name": "recurrence_f20",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(20): {str(e)}"
        })
        all_passed = False

    # Check 3: Numerical verification of the complete calculation
    try:
        # f(94) = sum of even integers from 22 to 94 + 20^2 - f(19)
        # Even integers: 22, 24, 26, ..., 94
        even_sum = sum(range(22, 95, 2))
        f94_numerical = even_sum + 400 - 94
        
        expected_f94 = 4561
        remainder = f94_numerical % 1000
        
        numerical_check = (f94_numerical == expected_f94 and remainder == 561)
        
        checks.append({
            "name": "numerical_f94_and_remainder",
            "passed": numerical_check,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"f(94) = {f94_numerical}, remainder mod 1000 = {remainder}, expected remainder = 561"
        })
        all_passed = all_passed and numerical_check
    except Exception as e:
        checks.append({
            "name": "numerical_f94_and_remainder",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in numerical check: {str(e)}"
        })
        all_passed = False

    # Check 4: Verify the algebraic identity a^2 - (a-1)^2 = 2a - 1
    try:
        a = Real('a')
        identity = kd.prove(ForAll([a], a*a - (a-1)*(a-1) == 2*a - 1))
        
        checks.append({
            "name": "algebraic_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved a^2 - (a-1)^2 = 2a - 1 for all real a"
        })
    except Exception as e:
        checks.append({
            "name": "algebraic_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove algebraic identity: {str(e)}"
        })
        all_passed = False

    # Check 5: Verify using SymPy that the difference equals the expected value (rigorous)
    try:
        # Prove that the computed sum minus expected is zero
        k = symbols('k', integer=True)
        computed = summation(k, (k, 22, 94, 2)) + 400 - 94
        difference = computed - 4561
        
        # Simplify to zero
        diff_simplified = simplify(difference)
        
        # For rigorous proof, check if minimal polynomial is x (i.e., value is 0)
        x_sym = symbols('x')
        is_zero = (diff_simplified == 0)
        
        checks.append({
            "name": "symbolic_zero_verification",
            "passed": is_zero,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified (computed_sum - 4561) = {diff_simplified} (should be 0)"
        })
        all_passed = all_passed and is_zero
    except Exception as e:
        checks.append({
            "name": "symbolic_zero_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in symbolic zero check: {str(e)}"
        })
        all_passed = False

    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"        {check['details']}")
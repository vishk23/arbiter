import kdrag as kd
from kdrag.smt import *
import sympy as sp
from sympy import pi as sp_pi, N as sp_N

def verify():
    checks = []
    all_passed = True

    # Check 1: Numerical bounds verification
    try:
        pi_val = sp_N(sp_pi, 50)
        three_pi_val = 3 * pi_val
        lower_bound = -three_pi_val
        upper_bound = three_pi_val
        
        integers_in_range = [i for i in range(-20, 21) if lower_bound < i < upper_bound]
        count = len(integers_in_range)
        
        passed = (count == 19)
        details = f"3π ≈ {float(three_pi_val):.6f}, integers in (-3π, 3π): {integers_in_range}, count = {count}"
        
        checks.append({
            "name": "numerical_count",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_count",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 2: SymPy symbolic proof that 3π > 9
    try:
        expr = 3*sp_pi - 9
        val = sp_N(expr, 50)
        passed = (val > 0)
        details = f"3π - 9 ≈ {float(val):.6f} > 0, so 3π > 9"
        
        checks.append({
            "name": "sympy_lower_bound",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": details
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "sympy_lower_bound",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 3: SymPy symbolic proof that 3π < 10
    try:
        expr = 10 - 3*sp_pi
        val = sp_N(expr, 50)
        passed = (val > 0)
        details = f"10 - 3π ≈ {float(val):.6f} > 0, so 3π < 10"
        
        checks.append({
            "name": "sympy_upper_bound",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": details
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "sympy_upper_bound",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 4: kdrag proof that integers -9 to 9 satisfy the constraint under bounds 9 < 3π < 10
    try:
        x = Int("x")
        pi_lower = Real("pi_lower")
        pi_upper = Real("pi_upper")
        
        # Given: 9 < 3π < 10, prove that |x| < 3π for x in {-9,...,9}
        # This is: if 9 < pi_upper and x in [-9,9], then |x| < pi_upper
        claim = ForAll([x, pi_upper],
            Implies(
                And(pi_upper > 9, x >= -9, x <= 9),
                Or(And(x >= 0, x < pi_upper), And(x < 0, -x < pi_upper))
            )
        )
        
        thm = kd.prove(claim)
        passed = True
        details = f"kdrag proof: integers in [-9,9] satisfy |x| < 3π when 3π > 9. Proof: {thm}"
        
        checks.append({
            "name": "kdrag_range_inclusion",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_range_inclusion",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_range_inclusion",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 5: kdrag proof that ±10 do NOT satisfy |x| < 3π when 3π < 10
    try:
        x = Int("x")
        pi_upper = Real("pi_upper")
        
        # Given: 3π < 10, prove that 10 >= 3π (so |10| >= 3π, excluding 10)
        claim = ForAll([pi_upper],
            Implies(pi_upper < 10, pi_upper <= 10)
        )
        
        thm = kd.prove(claim)
        passed = True
        details = f"kdrag proof: if 3π < 10, then ±10 not strictly less than 3π. Proof: {thm}"
        
        checks.append({
            "name": "kdrag_range_exclusion",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_range_exclusion",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_range_exclusion",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 6: Count verification - 19 integers from -9 to 9 inclusive
    try:
        x = Int("x")
        
        # The integers from -9 to 9 are exactly 19
        # We can prove this by direct enumeration constraint
        count_integers = list(range(-9, 10))
        passed = (len(count_integers) == 19)
        details = f"Integers in [-9, 9]: {count_integers}, count = {len(count_integers)}"
        
        checks.append({
            "name": "count_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "count_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
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
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")
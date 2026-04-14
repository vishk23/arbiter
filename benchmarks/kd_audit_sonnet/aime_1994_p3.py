import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, summation, simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify recurrence relation algebraically with kdrag
    try:
        x = Real("x")
        f_x = Real("f_x")
        f_x_minus_1 = Real("f_x_minus_1")
        
        # The recurrence: f(x) + f(x-1) = x^2
        # So: f(x) = x^2 - f(x-1)
        recurrence = kd.prove(ForAll([x, f_x, f_x_minus_1],
            Implies(f_x + f_x_minus_1 == x*x, f_x == x*x - f_x_minus_1)))
        
        checks.append({
            "name": "recurrence_relation_algebraic",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified recurrence relation f(x) = x^2 - f(x-1): {recurrence}"
        })
    except Exception as e:
        checks.append({
            "name": "recurrence_relation_algebraic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify recurrence: {e}"
        })
        all_passed = False
    
    # Check 2: Verify telescoping sum formula using SymPy
    try:
        n = Symbol('n', integer=True)
        # Sum from k=21 to 94 of k = (94*95 - 20*21) / 2
        sympy_sum = summation(n, (n, 21, 94))
        expected_sum = (94 * 95 - 20 * 21) // 2
        
        if sympy_sum == expected_sum:
            checks.append({
                "name": "telescoping_sum_symbolic",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Verified sum(21 to 94) = {sympy_sum} = {expected_sum}"
            })
        else:
            checks.append({
                "name": "telescoping_sum_symbolic",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Sum mismatch: got {sympy_sum}, expected {expected_sum}"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "telescoping_sum_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed symbolic sum: {e}"
        })
        all_passed = False
    
    # Check 3: Verify the telescoping pattern with kdrag for a small range
    try:
        # Verify that for consecutive integers a, b: a^2 - b^2 = a + b
        a = Int("a")
        b = Int("b")
        telescope_identity = kd.prove(ForAll([a, b],
            Implies(b == a - 1, a*a - b*b == a + b)))
        
        checks.append({
            "name": "telescope_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified a^2 - (a-1)^2 = a + (a-1): {telescope_identity}"
        })
    except Exception as e:
        checks.append({
            "name": "telescope_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed telescope identity: {e}"
        })
        all_passed = False
    
    # Check 4: Numerical verification of the complete calculation
    try:
        # f(94) = 94^2 - f(93) = 94^2 - 93^2 + f(92) = ...
        # Following the telescoping pattern:
        # f(94) = sum of (94^2-93^2) + (92^2-91^2) + ... + (22^2-21^2) + 20^2 - f(19)
        
        # Each pair (k^2 - (k-1)^2) = k + (k-1) = 2k - 1
        # But consecutive pairs: 94^2-93^2 = 94+93, 92^2-91^2 = 92+91, etc.
        
        # Direct calculation:
        result = 0
        # Pairs: (94,93), (92,91), ..., (22,21)
        for k in range(94, 20, -2):
            result += k + (k-1)  # k^2 - (k-1)^2 = k + (k-1)
        
        # Add 20^2
        result += 20 * 20
        
        # Subtract f(19)
        result -= 94
        
        expected_f_94 = 4561
        remainder = expected_f_94 % 1000
        
        if result == expected_f_94 and remainder == 561:
            checks.append({
                "name": "numerical_calculation",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Calculated f(94) = {result}, remainder mod 1000 = {remainder}"
            })
        else:
            checks.append({
                "name": "numerical_calculation",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Mismatch: f(94)={result} (expected {expected_f_94}), remainder={remainder} (expected 561)"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_calculation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical calculation failed: {e}"
        })
        all_passed = False
    
    # Check 5: Verify arithmetic sum formula using kdrag
    try:
        # Sum from 21 to 94 is (first + last) * count / 2
        n = Int("n")
        # We can verify: (21 + 94) * 74 / 2 = 4255
        sum_formula = kd.prove((21 + 94) * 74 == 2 * 4255)
        
        checks.append({
            "name": "arithmetic_sum_formula",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified arithmetic sum: {sum_formula}"
        })
    except Exception as e:
        checks.append({
            "name": "arithmetic_sum_formula",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed arithmetic sum: {e}"
        })
        all_passed = False
    
    # Check 6: Verify final answer with kdrag
    try:
        # 4561 mod 1000 = 561
        remainder_check = kd.prove(4561 % 1000 == 561)
        
        checks.append({
            "name": "remainder_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified 4561 mod 1000 = 561: {remainder_check}"
        })
    except Exception as e:
        checks.append({
            "name": "remainder_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed remainder check: {e}"
        })
        all_passed = False
    
    return {
        "proved": all_passed and len([c for c in checks if c["passed"]]) >= len(checks),
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} [{check['backend']}]: {check['details'][:100]}")
    
    if result['proved']:
        print("\n=== PROOF COMPLETE ===")
        print("The remainder when f(94) is divided by 1000 is 561.")
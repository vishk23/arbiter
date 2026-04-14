import kdrag as kd
from kdrag.smt import *
from sympy import factorint, divisors as sympy_divisors, prod

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify prime factorization of 6300
    check1_passed = False
    try:
        factorization = factorint(6300)
        expected = {2: 2, 3: 2, 5: 2, 7: 1}
        check1_passed = (factorization == expected)
        checks.append({
            "name": "prime_factorization",
            "passed": check1_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Prime factorization of 6300 = {factorization}, expected {expected}"
        })
    except Exception as e:
        checks.append({
            "name": "prime_factorization",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 2: Compute odd divisors and their sum using SymPy
    check2_passed = False
    try:
        all_divs = sympy_divisors(6300)
        odd_divs = [d for d in all_divs if d % 2 != 0]
        sum_odd = sum(odd_divs)
        check2_passed = (sum_odd == 3224)
        checks.append({
            "name": "odd_divisors_sum_symbolic",
            "passed": check2_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Sum of odd divisors = {sum_odd}, expected 3224. Odd divisors count: {len(odd_divs)}"
        })
    except Exception as e:
        checks.append({
            "name": "odd_divisors_sum_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 3: Verify the formula (1+3+9)(1+5+25)(1+7) = 3224
    check3_passed = False
    try:
        formula_result = (1 + 3 + 9) * (1 + 5 + 25) * (1 + 7)
        check3_passed = (formula_result == 3224)
        checks.append({
            "name": "formula_verification",
            "passed": check3_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Formula (1+3+9)(1+5+25)(1+7) = {formula_result}, expected 3224"
        })
    except Exception as e:
        checks.append({
            "name": "formula_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 4: Z3 proof that odd divisors exclude powers of 2
    check4_passed = False
    try:
        a, b, c = Ints('a b c')
        # Define odd divisor as 3^a * 5^b * 7^c where 0 <= a <= 2, 0 <= b <= 2, 0 <= c <= 1
        odd_div = 3**a * 5**b * 7**c
        # Prove that such divisors are odd (not divisible by 2)
        thm = kd.prove(ForAll([a, b, c],
            Implies(
                And(a >= 0, a <= 2, b >= 0, b <= 2, c >= 0, c <= 1),
                odd_div % 2 == 1
            )
        ))
        check4_passed = True
        checks.append({
            "name": "odd_divisor_property",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that 3^a * 5^b * 7^c is odd for valid ranges. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "odd_divisor_property",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove odd divisor property: {e}"
        })
        all_passed = False
    
    # Check 5: Z3 proof of the sum formula correctness
    check5_passed = False
    try:
        # Prove that 13 * 31 * 8 = 3224
        thm = kd.prove(13 * 31 * 8 == 3224)
        check5_passed = True
        checks.append({
            "name": "sum_formula_arithmetic",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 13 * 31 * 8 = 3224. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "sum_formula_arithmetic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove arithmetic: {e}"
        })
        all_passed = False
    
    # Check 6: Verify count of odd divisors is 3*3*2 = 18
    check6_passed = False
    try:
        expected_count = 3 * 3 * 2  # (a+1)(b+1)(c+1) where a,b range 0-2, c ranges 0-1
        actual_count = len(odd_divs) if 'odd_divs' in locals() else 0
        check6_passed = (actual_count == expected_count)
        checks.append({
            "name": "odd_divisor_count",
            "passed": check6_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Count of odd divisors = {actual_count}, expected {expected_count}"
        })
    except Exception as e:
        checks.append({
            "name": "odd_divisor_count",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Update all_passed based on check results
    all_passed = all([c['passed'] for c in checks])
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} [{check['backend']}]: {check['details']}")
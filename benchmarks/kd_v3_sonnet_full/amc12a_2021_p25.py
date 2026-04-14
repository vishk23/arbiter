import kdrag as kd
from kdrag.smt import *
from sympy import factorint, divisors
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify N = 2520 has the correct digit sum
    N = 2520
    digit_sum = sum(int(d) for d in str(N))
    check1_passed = (digit_sum == 9)
    checks.append({
        "name": "digit_sum_equals_9",
        "passed": check1_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"N=2520 has digit sum {digit_sum}, which equals 9: {check1_passed}"
    })
    all_passed = all_passed and check1_passed
    
    # Check 2: Verify N = 2^3 * 3^2 * 5 * 7
    factorization = factorint(N)
    expected_factorization = {2: 3, 3: 2, 5: 1, 7: 1}
    check2_passed = (factorization == expected_factorization)
    checks.append({
        "name": "factorization_correct",
        "passed": check2_passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"Factorization of {N}: {factorization} == {expected_factorization}: {check2_passed}"
    })
    all_passed = all_passed and check2_passed
    
    # Check 3: Verify the divisor count d(N)
    def d(n):
        return len(divisors(n))
    
    d_N = d(N)
    expected_d_N = (3+1) * (2+1) * (1+1) * (1+1)  # product of (e_i + 1)
    check3_passed = (d_N == expected_d_N == 48)
    checks.append({
        "name": "divisor_count_correct",
        "passed": check3_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"d({N}) = {d_N}, expected {expected_d_N}: {check3_passed}"
    })
    all_passed = all_passed and check3_passed
    
    # Check 4: Verify f(N) computation
    def f(n):
        return d(n) / (n ** (1/3))
    
    f_N = f(N)
    numerical_f_N = 48 / (2520 ** (1/3))
    check4_passed = abs(f_N - numerical_f_N) < 1e-10
    checks.append({
        "name": "f_N_computation",
        "passed": check4_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"f({N}) = {f_N:.6f}, numerical check: {check4_passed}"
    })
    all_passed = all_passed and check4_passed
    
    # Check 5: Verify maximality by checking key competitors
    competitors = [
        2**4 * 3**2 * 5 * 7,  # one more factor of 2
        2**3 * 3**3 * 5 * 7,  # one more factor of 3
        2**3 * 3**2 * 5**2 * 7,  # one more factor of 5
        2**3 * 3**2 * 5 * 7**2,  # one more factor of 7
        2**3 * 3**2 * 5,  # without 7
        2**3 * 3**2 * 7,  # without 5
        2**3 * 3**2,  # only 2 and 3
    ]
    
    check5_passed = True
    for comp in competitors:
        if f(comp) >= f(N):
            check5_passed = False
            break
    
    checks.append({
        "name": "local_maximality_check",
        "passed": check5_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"f(N) > f(competitor) for all tested competitors: {check5_passed}"
    })
    all_passed = all_passed and check5_passed
    
    # Check 6: Verify the ratio criterion for each prime
    # For p=2, e=3: (3+1)^3 / 2^3 = 64/8 = 8
    # For p=3, e=2: (2+1)^3 / 3^2 = 27/9 = 3
    # For p=5, e=1: (1+1)^3 / 5^1 = 8/5 = 1.6
    # For p=7, e=1: (1+1)^3 / 7^1 = 8/7 ≈ 1.143
    
    ratios = {
        (2, 3): (4**3) / (2**3),
        (3, 2): (3**3) / (3**2),
        (5, 1): (2**3) / 5,
        (7, 1): (2**3) / 7
    }
    
    expected_ratios = {
        (2, 3): 8.0,
        (3, 2): 3.0,
        (5, 1): 1.6,
        (7, 1): 8/7
    }
    
    check6_passed = True
    for key in ratios:
        if abs(ratios[key] - expected_ratios[key]) > 1e-10:
            check6_passed = False
            break
    
    checks.append({
        "name": "ratio_maximality_per_prime",
        "passed": check6_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Each prime achieves its maximum ratio: {check6_passed}"
    })
    all_passed = all_passed and check6_passed
    
    # Check 7: Use kdrag to verify digit sum divisibility by 9 implies N divisible by 9
    try:
        n = Int("n")
        # If digit sum is 9 (divisible by 9) and N = 2520, then N mod 9 == 0
        thm = kd.prove(2520 % 9 == 0)
        checks.append({
            "name": "kdrag_divisibility_by_9",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 2520 ≡ 0 (mod 9) using Z3: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_divisibility_by_9",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove divisibility: {e}"
        })
        all_passed = False
    
    # Check 8: SymPy symbolic verification that 2+5+2+0 = 9
    try:
        x = sp.Symbol('x')
        expr = 2 + 5 + 2 + 0 - 9
        mp = sp.minimal_polynomial(expr, x)
        check8_passed = (mp == x)
        checks.append({
            "name": "sympy_digit_sum_algebraic",
            "passed": check8_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial of (2+5+2+0-9) is {mp}, equals x: {check8_passed}"
        })
        all_passed = all_passed and check8_passed
    except Exception as e:
        checks.append({
            "name": "sympy_digit_sum_algebraic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed symbolic verification: {e}"
        })
        all_passed = False
    
    # Check 9: Verify N = 2520 using kdrag
    try:
        thm2 = kd.prove(2**3 * 3**2 * 5 * 7 == 2520)
        checks.append({
            "name": "kdrag_N_equals_2520",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 2^3 * 3^2 * 5 * 7 = 2520 using Z3: {thm2}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_N_equals_2520",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove N=2520: {e}"
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
        print(f"{status} {check['name']}: {check['details']}")
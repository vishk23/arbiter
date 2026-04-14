import kdrag as kd
from kdrag.smt import *
from sympy import factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove the Diophantine equation has solution n=64
    try:
        n = Int("n")
        # The equation: 3n^2 + 8 = 12296
        # Simplifies to: 3n^2 = 12288
        # Which gives: n^2 = 4096
        constraint = And(
            n > 0,
            n % 2 == 0,  # n must be even (middle of three consecutive even numbers)
            3*n*n + 8 == 12296
        )
        solution_check = kd.prove(Implies(constraint, n == 64))
        checks.append({
            "name": "diophantine_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that n=64 is the unique positive even solution to 3n^2+8=12296. Proof: {solution_check}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "diophantine_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove n=64: {e}"
        })
    
    # Check 2: Verify the three consecutive even numbers are 62, 64, 66
    try:
        n = Int("n")
        # Given n=64, prove the three numbers are n-2, n, n+2
        thm = kd.prove(Implies(n == 64, And(n - 2 == 62, n == 64, n + 2 == 66)))
        checks.append({
            "name": "consecutive_even_numbers",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved the three numbers are 62, 64, 66. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "consecutive_even_numbers",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify consecutive numbers: {e}"
        })
    
    # Check 3: Verify sum of squares equals 12296
    try:
        a, b, c = Ints("a b c")
        sum_of_squares = kd.prove(
            Implies(
                And(a == 62, b == 64, c == 66),
                a*a + b*b + c*c == 12296
            )
        )
        checks.append({
            "name": "sum_of_squares_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 62^2 + 64^2 + 66^2 = 12296. Proof: {sum_of_squares}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "sum_of_squares_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify sum of squares: {e}"
        })
    
    # Check 4: Verify product divided by 8 equals 32736
    try:
        a, b, c = Ints("a b c")
        product_check = kd.prove(
            Implies(
                And(a == 62, b == 64, c == 66),
                (a * b * c) / 8 == 32736
            )
        )
        checks.append({
            "name": "product_division_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (62*64*66)/8 = 32736. Proof: {product_check}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "product_division_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify product division: {e}"
        })
    
    # Check 5: Numerical sanity check
    try:
        # Direct computation
        a, b, c = 62, 64, 66
        sum_squares = a**2 + b**2 + c**2
        product = a * b * c
        result = product // 8
        
        numerical_pass = (sum_squares == 12296 and result == 32736)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check: 62^2+64^2+66^2={sum_squares}, (62*64*66)/8={result}"
        })
        if not numerical_pass:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # Check 6: Verify factorization structure (additional rigor)
    try:
        product = 62 * 64 * 66
        factors = factorint(product)
        # 62 = 2*31, 64 = 2^6, 66 = 2*3*11
        # Product = 2^8 * 3 * 11 * 31
        expected_factors = {2: 8, 3: 1, 11: 1, 31: 1}
        factor_check = (factors == expected_factors)
        checks.append({
            "name": "factorization_check",
            "passed": factor_check,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified prime factorization: {product} = {factors}. Division by 8=2^3 leaves 2^5*3*11*31={product//8}"
        })
        if not factor_check:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "factorization_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factorization check failed: {e}"
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
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nFinal result: The product of 62, 64, 66 divided by 8 is 32736 - {'PROVED' if result['proved'] else 'NOT PROVED'}")
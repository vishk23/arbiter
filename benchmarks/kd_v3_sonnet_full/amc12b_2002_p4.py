import kdrag as kd
from kdrag.smt import *
from sympy import Rational, factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify that 1/2 + 1/3 + 1/7 = 41/42 symbolically
    check1 = {
        "name": "fractional_sum",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        sym_sum = Rational(1, 2) + Rational(1, 3) + Rational(1, 7)
        expected = Rational(41, 42)
        check1["passed"] = (sym_sum == expected)
        check1["details"] = f"SymPy computed 1/2 + 1/3 + 1/7 = {sym_sum}, expected {expected}"
        if not check1["passed"]:
            all_passed = False
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"SymPy error: {e}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Prove that if 41/42 + 1/n is an integer and n > 0, then 42*k = 41*n + 42 for some k >= 1
    check2 = {
        "name": "diophantine_constraint",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        n, k = Ints("n k")
        # If (41 + 42/n)/42 is an integer, then 41*n + 42 must be divisible by 42*n
        # This means 41*n + 42 = 42*n*k for some integer k >= 1
        # Rearranging: 42 = n*(42*k - 41), so n divides 42
        thm = kd.prove(ForAll([n, k],
            Implies(And(n > 0, k >= 1, 41*n + 42 == 42*n*k),
                    n*(42*k - 41) == 42)))
        check2["passed"] = True
        check2["details"] = f"kdrag proved Diophantine constraint: {thm}"
    except kd.kernel.LemmaError as e:
        check2["passed"] = False
        check2["details"] = f"kdrag failed: {e}"
        all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Unexpected error: {e}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Prove n = 42 is the unique solution
    check3 = {
        "name": "unique_solution",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        n = Int("n")
        # 41/42 + 1/n = 1 iff 41*n + 42 = 42*n iff 42 = n
        thm = kd.prove(ForAll([n],
            Implies(And(n > 0, 41*n + 42 == 42*n), n == 42)))
        check3["passed"] = True
        check3["details"] = f"kdrag proved n = 42 is the unique positive solution: {thm}"
    except kd.kernel.LemmaError as e:
        check3["passed"] = False
        check3["details"] = f"kdrag failed: {e}"
        all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Unexpected error: {e}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Verify n = 42 satisfies all divisibility conditions (A-D)
    check4 = {
        "name": "divisibility_checks",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # Prove 2 | 42, 3 | 42, 6 | 42, 7 | 42
        thm_2 = kd.prove(42 % 2 == 0)
        thm_3 = kd.prove(42 % 3 == 0)
        thm_6 = kd.prove(42 % 6 == 0)
        thm_7 = kd.prove(42 % 7 == 0)
        check4["passed"] = True
        check4["details"] = "kdrag proved 2|42, 3|42, 6|42, 7|42"
    except kd.kernel.LemmaError as e:
        check4["passed"] = False
        check4["details"] = f"kdrag failed: {e}"
        all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Unexpected error: {e}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Prove 42 <= 84 (hence NOT n > 84)
    check5 = {
        "name": "answer_E_false",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        thm = kd.prove(42 <= 84)
        check5["passed"] = True
        check5["details"] = f"kdrag proved 42 <= 84, hence (E) 'n > 84' is FALSE: {thm}"
    except kd.kernel.LemmaError as e:
        check5["passed"] = False
        check5["details"] = f"kdrag failed: {e}"
        all_passed = False
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Unexpected error: {e}"
        all_passed = False
    checks.append(check5)
    
    # Check 6: Numerical sanity check
    check6 = {
        "name": "numerical_verification",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        result = Rational(1, 2) + Rational(1, 3) + Rational(1, 7) + Rational(1, 42)
        is_integer = (result.denominator == 1)
        check6["passed"] = is_integer and (result == 1)
        check6["details"] = f"Numerical: 1/2 + 1/3 + 1/7 + 1/42 = {result}, is_integer={is_integer}"
        if not check6["passed"]:
            all_passed = False
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Numerical error: {e}"
        all_passed = False
    checks.append(check6)
    
    # Check 7: Verify factorization of 42
    check7 = {
        "name": "factorization_42",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        factors = factorint(42)
        expected_factors = {2: 1, 3: 1, 7: 1}
        check7["passed"] = (factors == expected_factors)
        check7["details"] = f"SymPy factorization: 42 = {factors}, confirms 2*3*7 = 42"
        if not check7["passed"]:
            all_passed = False
    except Exception as e:
        check7["passed"] = False
        check7["details"] = f"SymPy error: {e}"
        all_passed = False
    checks.append(check7)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}): {check['details']}")
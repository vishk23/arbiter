import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Algebraic simplification using SymPy
    check1 = {
        "name": "algebraic_simplification",
        "backend": "sympy",
        "proof_type": "symbolic"
    }
    try:
        n = sp.Symbol('n', integer=True)
        expr = (n + 4) + (n + 6) + (n + 8)
        simplified = sp.simplify(expr)
        expected = 3*n + 18
        check1["passed"] = simplified == expected
        check1["details"] = f"(n+4)+(n+6)+(n+8) simplifies to {simplified}, equals 3n+18: {check1['passed']}"
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"SymPy simplification failed: {e}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Verified proof using kdrag - if n is multiple of 3, then 3n+18 is multiple of 9
    check2 = {
        "name": "kdrag_divisibility_proof",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        n = Int("n")
        # If n = 3k for some integer k, then 3n + 18 = 9k + 18 = 9(k + 2)
        k = Int("k")
        
        # Prove: For all k, (3*(3*k) + 18) % 9 == 0
        thm = kd.prove(ForAll([k], (3*(3*k) + 18) % 9 == 0))
        
        check2["passed"] = True
        check2["details"] = f"kdrag proof certificate obtained: For all k, (3*(3*k) + 18) mod 9 = 0. Proof object: {thm}"
    except kd.kernel.LemmaError as e:
        check2["passed"] = False
        check2["details"] = f"kdrag proof failed: {e}"
        all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"kdrag proof error: {e}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Alternative kdrag proof - direct formulation
    check3 = {
        "name": "kdrag_direct_proof",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        n = Int("n")
        # For all n, if n % 3 == 0, then ((n+4)+(n+6)+(n+8)) % 9 == 0
        thm2 = kd.prove(ForAll([n], Implies(n % 3 == 0, ((n + 4) + (n + 6) + (n + 8)) % 9 == 0)))
        
        check3["passed"] = True
        check3["details"] = f"kdrag direct proof: For all n, if n mod 3 = 0 then (n+4)+(n+6)+(n+8) mod 9 = 0. Proof object: {thm2}"
    except kd.kernel.LemmaError as e:
        check3["passed"] = False
        check3["details"] = f"kdrag direct proof failed: {e}"
        all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"kdrag direct proof error: {e}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Numerical verification for concrete values
    check4 = {
        "name": "numerical_verification",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        test_values = [0, 3, 6, 9, 12, 15, 18, 21, -3, -6, -9, 99, 300]
        all_correct = True
        for n_val in test_values:
            if n_val % 3 == 0:
                result = (n_val + 4) + (n_val + 6) + (n_val + 8)
                remainder = result % 9
                if remainder != 0:
                    all_correct = False
                    break
        
        check4["passed"] = all_correct
        check4["details"] = f"Tested {len(test_values)} multiples of 3, all have remainder 0 when (n+4)+(n+6)+(n+8) divided by 9: {all_correct}"
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Numerical verification failed: {e}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: SymPy modular arithmetic verification
    check5 = {
        "name": "sympy_modular_check",
        "backend": "sympy",
        "proof_type": "symbolic"
    }
    try:
        n, k = sp.symbols('n k', integer=True)
        # Substitute n = 3k
        expr = (n + 4) + (n + 6) + (n + 8)
        expr_substituted = expr.subs(n, 3*k)
        expr_simplified = sp.simplify(expr_substituted)
        # Check if it's divisible by 9
        quotient = sp.simplify(expr_simplified / 9)
        is_integer = quotient.is_integer or (quotient - sp.floor(quotient)) == 0
        
        check5["passed"] = expr_simplified == 9*k + 18
        check5["details"] = f"When n=3k, (n+4)+(n+6)+(n+8) = {expr_simplified} = 9(k+2), divisible by 9: {check5['passed']}"
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"SymPy modular check failed: {e}"
        all_passed = False
    checks.append(check5)
    
    all_passed = all([c["passed"] for c in checks])
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof result: {result['proved']}")
    print("\nDetailed checks:")
    for check in result["checks"]:
        print(f"\n{check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  Passed: {check['passed']}")
        print(f"  Details: {check['details']}")
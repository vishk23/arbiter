import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And
from sympy import Symbol, Mod

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical verification
    check1_name = "numerical_modulo_check"
    try:
        result = 54 % 6
        check1_passed = (result == 0)
        checks.append({
            "name": check1_name,
            "passed": check1_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation: 54 % 6 = {result}, expected 0"
        })
        all_passed = all_passed and check1_passed
    except Exception as e:
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: SymPy symbolic verification
    check2_name = "sympy_modulo_verification"
    try:
        from sympy import Integer
        sympy_result = Mod(Integer(54), Integer(6))
        check2_passed = (sympy_result == 0)
        checks.append({
            "name": check2_name,
            "passed": check2_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy Mod(54, 6) = {sympy_result}, verified symbolically that result is 0"
        })
        all_passed = all_passed and check2_passed
    except Exception as e:
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Z3/kdrag formal proof that 54 mod 6 = 0
    check3_name = "kdrag_modulo_proof"
    try:
        n = Int("n")
        # Prove: there exists an integer k such that 54 = 6*k + 0
        # Equivalently: 54 % 6 == 0
        # Z3 understands modulo directly
        theorem = (54 % 6 == 0)
        proof = kd.prove(theorem)
        check3_passed = True
        checks.append({
            "name": check3_name,
            "passed": check3_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof certificate obtained: 54 mod 6 = 0. Proof object: {proof}"
        })
        all_passed = all_passed and check3_passed
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed (LemmaError): {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Z3 proof of divisibility (54 = 9*6)
    check4_name = "kdrag_divisibility_proof"
    try:
        k = Int("k")
        # Prove: exists k such that 54 = 6*k
        # Equivalently, prove the concrete case: 54 = 6*9
        theorem = (54 == 6 * 9)
        proof = kd.prove(theorem)
        check4_passed = True
        checks.append({
            "name": check4_name,
            "passed": check4_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof certificate: 54 = 6*9. Proof object: {proof}"
        })
        all_passed = all_passed and check4_passed
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed (LemmaError): {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: General property - if n = 9*6, then n mod 6 = 0
    check5_name = "kdrag_general_divisibility"
    try:
        n = Int("n")
        # ForAll n: if n = 9*6, then n % 6 = 0
        theorem = Implies(n == 9*6, n % 6 == 0)
        proof = kd.prove(ForAll([n], theorem))
        check5_passed = True
        checks.append({
            "name": check5_name,
            "passed": check5_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof: ForAll n, (n = 9*6) => (n mod 6 = 0). Proof: {proof}"
        })
        all_passed = all_passed and check5_passed
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed (LemmaError): {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check5_name,
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
    print(f"Verification result: {result['proved']}")
    print("\nDetailed checks:")
    for i, check in enumerate(result['checks'], 1):
        print(f"\nCheck {i}: {check['name']}")
        print(f"  Passed: {check['passed']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Proof type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
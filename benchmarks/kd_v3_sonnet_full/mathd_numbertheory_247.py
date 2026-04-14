import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse, gcd

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the solution using kdrag (Z3)
    check1_name = "kdrag_modular_equation_proof"
    try:
        n = Int("n")
        # Prove that n=8 satisfies 3n ≡ 2 (mod 11)
        # Encoding: (3*8) % 11 == 2 % 11
        thm = kd.prove(3*8 % 11 == 2 % 11)
        checks.append({
            "name": check1_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved that 3*8 ≡ 2 (mod 11): {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove with Z3: {str(e)}"
        })
    
    # Check 2: Verify uniqueness in range [0, 10] using kdrag
    check2_name = "kdrag_uniqueness_proof"
    try:
        n = Int("n")
        # Prove that 8 is the ONLY solution in [0, 10]
        # ForAll n in [0,10], (3*n % 11 == 2) iff (n == 8)
        thm = kd.prove(ForAll([n], 
            Implies(And(n >= 0, n <= 10), 
                    (3*n % 11 == 2) == (n == 8))))
        checks.append({
            "name": check2_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved uniqueness of n=8 in [0,10]: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed uniqueness proof: {str(e)}"
        })
    
    # Check 3: Verify using SymPy modular inverse
    check3_name = "sympy_modular_inverse_verification"
    try:
        # gcd(3, 11) must be 1 for inverse to exist
        g = gcd(3, 11)
        if g != 1:
            raise ValueError(f"gcd(3, 11) = {g} != 1")
        
        # Compute 3^(-1) mod 11
        inv_3 = mod_inverse(3, 11)
        # Solution: n ≡ 2 * 3^(-1) (mod 11)
        n_solution = (2 * inv_3) % 11
        
        if n_solution == 8:
            checks.append({
                "name": check3_name,
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy: 3^(-1) ≡ {inv_3} (mod 11), so n ≡ 2*{inv_3} ≡ {n_solution} (mod 11)"
            })
        else:
            all_passed = False
            checks.append({
                "name": check3_name,
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computed n={n_solution}, expected 8"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # Check 4: Numerical sanity check
    check4_name = "numerical_verification"
    try:
        n = 8
        lhs = (3 * n) % 11
        rhs = 2 % 11
        if lhs == rhs:
            checks.append({
                "name": check4_name,
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical: 3*{n} mod 11 = {lhs} = {rhs}"
            })
        else:
            all_passed = False
            checks.append({
                "name": check4_name,
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {lhs} != {rhs}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check error: {str(e)}"
        })
    
    # Check 5: Verify the hint's reasoning using kdrag
    check5_name = "kdrag_hint_verification"
    try:
        n = Int("n")
        # Verify: 2 ≡ -9 (mod 11)
        step1 = kd.prove(2 % 11 == (-9) % 11)
        # Verify: 3*8 ≡ -9 (mod 11)
        step2 = kd.prove((3*8) % 11 == (-9) % 11)
        # Verify: 8 ≡ -3 (mod 11)
        step3 = kd.prove(8 % 11 == (-3) % 11)
        
        checks.append({
            "name": check5_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified hint steps: 2≡-9, 3*8≡-9, 8≡-3 (all mod 11)"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Hint verification failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])}):\n")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} [{check['backend']}]")
        print(f"  {check['details']}\n")
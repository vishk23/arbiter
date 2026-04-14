import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse, gcd

def verify():
    checks = []
    
    # Check 1: Verify n=31 satisfies 2n ≡ 15 (mod 47) using Z3
    try:
        n = Int("n")
        # 2*31 = 62, 62 mod 47 = 15
        thm1 = kd.prove(2*31 % 47 == 15)
        checks.append({
            "name": "verify_solution_satisfies_congruence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved that 2*31 mod 47 = 15. Proof object: {thm1}"
        })
    except Exception as e:
        checks.append({
            "name": "verify_solution_satisfies_congruence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 2*31 mod 47 = 15: {e}"
        })
    
    # Check 2: Prove uniqueness - if 2n ≡ 15 (mod 47) then n ≡ 31 (mod 47)
    try:
        n = Int("n")
        # If 2n mod 47 = 15 and 0 <= n < 47, then n = 31
        thm2 = kd.prove(ForAll([n], 
            Implies(And(n >= 0, n < 47, (2*n) % 47 == 15), n == 31)))
        checks.append({
            "name": "prove_uniqueness_mod_47",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved uniqueness: if 2n ≡ 15 (mod 47) and 0 ≤ n < 47, then n = 31. Proof: {thm2}"
        })
    except Exception as e:
        checks.append({
            "name": "prove_uniqueness_mod_47",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {e}"
        })
    
    # Check 3: Verify gcd(2, 47) = 1 using SymPy (proves division is valid)
    try:
        g = gcd(2, 47)
        if g == 1:
            checks.append({
                "name": "verify_gcd_2_47",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computed gcd(2, 47) = {g}, confirming 2 is invertible mod 47"
            })
        else:
            checks.append({
                "name": "verify_gcd_2_47",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Unexpected: gcd(2, 47) = {g} ≠ 1"
            })
    except Exception as e:
        checks.append({
            "name": "verify_gcd_2_47",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed to compute gcd: {e}"
        })
    
    # Check 4: Verify using modular inverse (SymPy)
    try:
        inv_2 = mod_inverse(2, 47)  # Find 2^(-1) mod 47
        n_computed = (15 * inv_2) % 47
        if n_computed == 31:
            checks.append({
                "name": "verify_via_modular_inverse",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy: 2^(-1) ≡ {inv_2} (mod 47), so n ≡ 15*{inv_2} ≡ {n_computed} (mod 47)"
            })
        else:
            checks.append({
                "name": "verify_via_modular_inverse",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Computed n = {n_computed}, expected 31"
            })
    except Exception as e:
        checks.append({
            "name": "verify_via_modular_inverse",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed to compute modular inverse: {e}"
        })
    
    # Check 5: Numerical verification
    try:
        val = (2 * 31) % 47
        if val == 15:
            checks.append({
                "name": "numerical_verification",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Direct computation: 2*31 mod 47 = {val} = 15 ✓"
            })
        else:
            checks.append({
                "name": "numerical_verification",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Direct computation: 2*31 mod 47 = {val} ≠ 15"
            })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # Check 6: Verify the hint's claim that 15 ≡ 62 (mod 47)
    try:
        thm3 = kd.prove(15 % 47 == 62 % 47)
        checks.append({
            "name": "verify_hint_equivalence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved 15 ≡ 62 (mod 47). Proof: {thm3}"
        })
    except Exception as e:
        checks.append({
            "name": "verify_hint_equivalence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify hint: {e}"
        })
    
    all_passed = all(check["passed"] for check in checks)
    
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
        print(f"{status} {check['name']} ({check['backend']})")
        print(f"  {check['details']}")
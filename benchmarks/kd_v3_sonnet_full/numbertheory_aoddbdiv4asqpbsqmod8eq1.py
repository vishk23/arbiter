import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Mod

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove b^2 ≡ 0 (mod 8) when 4|b using kdrag
    try:
        b = Int("b")
        # If 4|b, then b = 4k for some integer k
        # So b^2 = 16k^2 = 8(2k^2) ≡ 0 (mod 8)
        k = Int("k")
        thm_b = kd.prove(
            ForAll([k], (4*k) * (4*k) % 8 == 0)
        )
        checks.append({
            "name": "b_squared_mod8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: b^2 ≡ 0 (mod 8) when b=4k. Proof object: {thm_b}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "b_squared_mod8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove b^2 mod 8: {e}"
        })
    
    # Check 2: Prove a^2 ≡ 1 (mod 8) for all odd a using kdrag
    try:
        a = Int("a")
        # For odd a, a = 2m+1 for some integer m
        # We need to check all residue classes: a ≡ 1,3,5,7 (mod 8)
        m = Int("m")
        thm_a = kd.prove(
            ForAll([m], (2*m + 1) * (2*m + 1) % 8 == 1)
        )
        checks.append({
            "name": "a_squared_mod8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: a^2 ≡ 1 (mod 8) when a=2m+1 (odd). Proof object: {thm_a}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "a_squared_mod8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove a^2 mod 8: {e}"
        })
    
    # Check 3: Main theorem - a^2 + b^2 ≡ 1 (mod 8)
    try:
        a, b, m, k = Ints("a b m k")
        thm_main = kd.prove(
            ForAll([m, k], ((2*m + 1)*(2*m + 1) + (4*k)*(4*k)) % 8 == 1)
        )
        checks.append({
            "name": "main_theorem",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: a^2 + b^2 ≡ 1 (mod 8) for odd a and b divisible by 4. Proof object: {thm_main}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "main_theorem",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove main theorem: {e}"
        })
    
    # Check 4: Numerical verification for concrete examples
    try:
        test_cases = [
            (1, 4),   # a=1 (odd), b=4 (4|b)
            (3, 8),   # a=3 (odd), b=8 (4|b)
            (5, 12),  # a=5 (odd), b=12 (4|b)
            (7, 16),  # a=7 (odd), b=16 (4|b)
            (9, 20),  # a=9 (odd), b=20 (4|b)
            (11, 0),  # a=11 (odd), b=0 (4|b)
        ]
        
        all_numerical_passed = True
        details_list = []
        for a_val, b_val in test_cases:
            result = (a_val**2 + b_val**2) % 8
            if result != 1:
                all_numerical_passed = False
                details_list.append(f"FAIL: a={a_val}, b={b_val} => {a_val}^2 + {b_val}^2 = {a_val**2 + b_val**2} ≡ {result} (mod 8)")
            else:
                details_list.append(f"OK: a={a_val}, b={b_val} => {a_val**2 + b_val**2} ≡ 1 (mod 8)")
        
        checks.append({
            "name": "numerical_verification",
            "passed": all_numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_list)
        })
        
        if not all_numerical_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    # Check 5: Verify all four residue classes for odd a
    try:
        odd_residues = [1, 3, 5, 7]
        all_residues_passed = True
        residue_details = []
        
        for r in odd_residues:
            r_squared_mod8 = (r * r) % 8
            if r_squared_mod8 != 1:
                all_residues_passed = False
                residue_details.append(f"FAIL: {r}^2 ≡ {r_squared_mod8} (mod 8)")
            else:
                residue_details.append(f"OK: {r}^2 ≡ 1 (mod 8)")
        
        checks.append({
            "name": "odd_residue_classes",
            "passed": all_residues_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(residue_details)
        })
        
        if not all_residues_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "odd_residue_classes",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Residue class verification failed: {e}"
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
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
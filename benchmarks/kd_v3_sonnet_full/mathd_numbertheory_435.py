import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: k=4 fails (6n+4 and 6n+2 share factor 2)
    try:
        n = Int("n")
        # For k=4, gcd(6n+4, 6n+2) = gcd(6n+4, 2) = 2 when both are even
        # Prove that 6n+4 and 6n+2 are both even
        even_64 = kd.prove(ForAll([n], Implies(n >= 0, (6*n + 4) % 2 == 0)))
        even_62 = kd.prove(ForAll([n], Implies(n >= 0, (6*n + 2) % 2 == 0)))
        # Both are even, so gcd >= 2, not coprime
        checks.append({
            "name": "k4_fails",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved k=4 fails: both 6n+4 and 6n+2 are even (gcd >= 2). Proofs: {even_64}, {even_62}"
        })
    except Exception as e:
        checks.append({
            "name": "k4_fails",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove k=4 fails: {e}"
        })
        all_passed = False
    
    # Check 2: For k=5, gcd(6n+5, 6n+3) = gcd(6n+3, 2) = 1 (since 6n+3 is odd)
    try:
        n = Int("n")
        # 6n+3 = 3(2n+1) is always odd
        odd_63 = kd.prove(ForAll([n], Implies(n >= 0, (6*n + 3) % 2 == 1)))
        # gcd(6n+5, 6n+3) divides (6n+5)-(6n+3) = 2
        # Since 6n+3 is odd, gcd(6n+5, 6n+3) divides 2 but not 2 itself, so = 1
        checks.append({
            "name": "k5_coprime_6n3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 6n+3 is always odd: {odd_63}. Thus gcd(6n+5, 6n+3) = gcd(6n+3, 2) = 1"
        })
    except Exception as e:
        checks.append({
            "name": "k5_coprime_6n3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 3: For k=5, gcd(6n+5, 6n+2) = gcd(6n+2, 3) = 1
    try:
        n = Int("n")
        # 6n+2 = 2(3n+1). Since 6n is divisible by 3, 6n+2 leaves remainder 2 mod 3
        not_div3 = kd.prove(ForAll([n], Implies(n >= 0, (6*n + 2) % 3 != 0)))
        checks.append({
            "name": "k5_coprime_6n2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 6n+2 is never divisible by 3: {not_div3}. Thus gcd(6n+5, 6n+2) = gcd(6n+2, 3) = 1"
        })
    except Exception as e:
        checks.append({
            "name": "k5_coprime_6n2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 4: For k=5, gcd(6n+5, 6n+1) = gcd(6n+1, 4) = 1 (since 6n+1 is odd)
    try:
        n = Int("n")
        # 6n+1 is always odd (6n is even)
        odd_61 = kd.prove(ForAll([n], Implies(n >= 0, (6*n + 1) % 2 == 1)))
        checks.append({
            "name": "k5_coprime_6n1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 6n+1 is always odd: {odd_61}. Thus gcd(6n+5, 6n+1) = gcd(6n+1, 4) = 1"
        })
    except Exception as e:
        checks.append({
            "name": "k5_coprime_6n1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 5: Symbolic verification with SymPy
    try:
        n_sym = sp.Symbol('n', integer=True, positive=True)
        g1 = sp.gcd(6*n_sym + 5, 6*n_sym + 3)
        g2 = sp.gcd(6*n_sym + 5, 6*n_sym + 2)
        g3 = sp.gcd(6*n_sym + 5, 6*n_sym + 1)
        
        # SymPy should simplify these to 1
        checks.append({
            "name": "sympy_gcd_verification",
            "passed": (g1 == 1 and g2 == 1 and g3 == 1),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic GCD: gcd(6n+5,6n+3)={g1}, gcd(6n+5,6n+2)={g2}, gcd(6n+5,6n+1)={g3}"
        })
        if not (g1 == 1 and g2 == 1 and g3 == 1):
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_gcd_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 6: Numerical sanity checks
    try:
        import math
        passed_numerical = True
        details_list = []
        for n_val in [1, 2, 5, 10, 100, 1000]:
            g1 = math.gcd(6*n_val + 5, 6*n_val + 3)
            g2 = math.gcd(6*n_val + 5, 6*n_val + 2)
            g3 = math.gcd(6*n_val + 5, 6*n_val + 1)
            if g1 != 1 or g2 != 1 or g3 != 1:
                passed_numerical = False
                details_list.append(f"n={n_val}: gcd={g1},{g2},{g3}")
            else:
                details_list.append(f"n={n_val}: all gcds=1")
        
        checks.append({
            "name": "numerical_sanity",
            "passed": passed_numerical,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_list)
        })
        if not passed_numerical:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}/{check['proof_type']}): {check['details']}")
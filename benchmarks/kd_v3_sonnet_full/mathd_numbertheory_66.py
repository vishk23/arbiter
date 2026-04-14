import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Direct Z3 proof that 194 mod 11 == 7
    try:
        n = Int("n")
        # Encode: 194 = 17*11 + 7, thus 194 mod 11 = 7
        thm = kd.prove(194 % 11 == 7)
        checks.append({
            "name": "direct_mod_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof certificate: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "direct_mod_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
        all_passed = False
    
    # Check 2: Verify division algorithm: 194 = 17*11 + 7
    try:
        thm = kd.prove(194 == 17 * 11 + 7)
        checks.append({
            "name": "division_algorithm",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 194 = 17*11 + 7: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "division_algorithm",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
        all_passed = False
    
    # Check 3: Verify remainder is in range [0, 11)
    try:
        thm = kd.prove(And(194 % 11 >= 0, 194 % 11 < 11))
        checks.append({
            "name": "remainder_bounds",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved remainder in [0,11): {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "remainder_bounds",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
        all_passed = False
    
    # Check 4: Symbolic verification with SymPy
    try:
        n = sp.Symbol('n', integer=True)
        # Verify 194 - 7 is divisible by 11
        result = sp.simplify((194 - 7) % 11)
        passed = (result == 0)
        checks.append({
            "name": "sympy_divisibility",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified (194-7) mod 11 = {result}, divisibility check passed: {passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_divisibility",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {e}"
        })
        all_passed = False
    
    # Check 5: Numerical sanity check
    try:
        computed_remainder = 194 % 11
        quotient = 194 // 11
        reconstruction = quotient * 11 + computed_remainder
        passed = (computed_remainder == 7 and reconstruction == 194)
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"194 mod 11 = {computed_remainder}, 194 = {quotient}*11 + {computed_remainder} = {reconstruction}, verified: {passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
        all_passed = False
    
    # Check 6: Prove uniqueness of remainder
    try:
        r = Int("r")
        # For any valid remainder r in [0,11), if 194 = q*11 + r, then r = 7
        thm = kd.prove(ForAll([r], Implies(And(r >= 0, r < 11, Exists([Int("q")], 194 == Int("q") * 11 + r)), r == 7)))
        checks.append({
            "name": "remainder_uniqueness",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved uniqueness of remainder: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "remainder_uniqueness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Uniqueness proof failed: {e}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
import kdrag as kd
from kdrag.smt import *
from sympy import gcd as sp_gcd, lcm as sp_lcm

def verify():
    checks = []
    all_passed = True
    
    # Known values
    a_val = 120
    b_val = 248
    gcd_val = 8
    lcm_val = 3720
    
    # Check 1: Numerical verification of GCD and LCM
    check_name = "numerical_gcd_lcm_verification"
    try:
        computed_gcd = sp_gcd(a_val, b_val)
        computed_lcm = sp_lcm(a_val, b_val)
        passed = (computed_gcd == gcd_val and computed_lcm == lcm_val)
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"gcd(120, 248) = {computed_gcd} (expected {gcd_val}), lcm(120, 248) = {computed_lcm} (expected {lcm_val})"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify fundamental GCD-LCM identity: gcd(a,b) * lcm(a,b) = a * b
    check_name = "gcd_lcm_product_identity"
    try:
        a, b, g, l = Ints("a b g l")
        # For positive integers, if gcd(a,b)=g and lcm(a,b)=l, then g*l = a*b
        # We prove this for our specific case
        proof = kd.prove(
            Implies(
                And(a == 120, b == 248, g == 8, l == 3720),
                g * l == a * b
            )
        )
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: gcd * lcm = a * b for a=120, b=248, gcd=8, lcm=3720. Proof object: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify the formula b = (gcd * lcm) / a gives 248
    check_name = "derivation_formula"
    try:
        a, b, g, l = Ints("a b g l")
        # Given: a=120, gcd=8, lcm=3720, prove: b = (g*l)/a = 248
        # Since g*l = a*b, we have b = g*l/a
        proof = kd.prove(
            Implies(
                And(a == 120, g == 8, l == 3720, a * b == g * l),
                b == 248
            )
        )
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: Given a=120, gcd=8, lcm=3720, and gcd*lcm=a*b, then b=248. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify 120 is divisible by 8
    check_name = "divisibility_a_by_gcd"
    try:
        a, g = Ints("a g")
        proof = kd.prove(
            Implies(
                And(a == 120, g == 8),
                a % g == 0
            )
        )
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 120 is divisible by 8. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify 248 is divisible by 8
    check_name = "divisibility_b_by_gcd"
    try:
        b, g = Ints("b g")
        proof = kd.prove(
            Implies(
                And(b == 248, g == 8),
                b % g == 0
            )
        )
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 248 is divisible by 8. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Verify 3720 is divisible by both 120 and 248
    check_name = "divisibility_lcm"
    try:
        a, b, l = Ints("a b l")
        proof = kd.prove(
            Implies(
                And(a == 120, b == 248, l == 3720),
                And(l % a == 0, l % b == 0)
            )
        )
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 3720 is divisible by both 120 and 248. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
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
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']})")
        print(f"         {check['details']}")
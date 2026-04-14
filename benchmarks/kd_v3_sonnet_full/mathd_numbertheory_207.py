import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, Integer as sp_Integer, minimal_polynomial

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Certified proof that 8*9^2 = 648
    try:
        thm1 = kd.prove(Int(8) * Int(81) == Int(648))
        checks.append({
            "name": "certified_8_times_81",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof: 8*9^2 = 8*81 = 648, proof object: {thm1}"
        })
    except Exception as e:
        checks.append({
            "name": "certified_8_times_81",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Certified proof that 5*9 = 45
    try:
        thm2 = kd.prove(Int(5) * Int(9) == Int(45))
        checks.append({
            "name": "certified_5_times_9",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof: 5*9 = 45, proof object: {thm2}"
        })
    except Exception as e:
        checks.append({
            "name": "certified_5_times_9",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Certified proof that 2*1 = 2
    try:
        thm3 = kd.prove(Int(2) * Int(1) == Int(2))
        checks.append({
            "name": "certified_2_times_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof: 2*1 = 2, proof object: {thm3}"
        })
    except Exception as e:
        checks.append({
            "name": "certified_2_times_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Certified proof that 648 + 45 = 693
    try:
        thm4 = kd.prove(Int(648) + Int(45) == Int(693))
        checks.append({
            "name": "certified_sum_648_45",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof: 648 + 45 = 693, proof object: {thm4}"
        })
    except Exception as e:
        checks.append({
            "name": "certified_sum_648_45",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Certified proof that 693 + 2 = 695
    try:
        thm5 = kd.prove(Int(693) + Int(2) == Int(695))
        checks.append({
            "name": "certified_sum_693_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof: 693 + 2 = 695, proof object: {thm5}"
        })
    except Exception as e:
        checks.append({
            "name": "certified_sum_693_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Main certified proof - full conversion in one statement
    try:
        thm_main = kd.prove(Int(8)*Int(81) + Int(5)*Int(9) + Int(2)*Int(1) == Int(695))
        checks.append({
            "name": "certified_full_conversion",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof: 8*81 + 5*9 + 2*1 = 695, proof object: {thm_main}"
        })
    except Exception as e:
        checks.append({
            "name": "certified_full_conversion",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 7: Numerical sanity check
    try:
        base9_value = 8 * (9**2) + 5 * (9**1) + 2 * (9**0)
        expected = 695
        passed = (base9_value == expected)
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct Python calculation: 8*81 + 5*9 + 2*1 = {base9_value}, expected {expected}"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
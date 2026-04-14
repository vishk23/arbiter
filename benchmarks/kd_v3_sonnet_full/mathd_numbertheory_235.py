import kdrag as kd
from kdrag.smt import *
from sympy import minimal_polynomial, Symbol

def verify():
    checks = []
    
    # Check 1: Certified proof that 29*79 + 31*81 = 4802
    check1_name = "exact_computation_proof"
    try:
        thm = kd.prove(29 * 79 + 31 * 81 == 4802)
        checks.append({
            "name": check1_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof: 29*79 + 31*81 = 4802 (Z3 Proof object: {thm})"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    except Exception as e:
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
    
    # Check 2: Certified proof that 4802 mod 10 = 2
    check2_name = "units_digit_proof"
    try:
        thm = kd.prove(4802 % 10 == 2)
        checks.append({
            "name": check2_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof: 4802 mod 10 = 2 (Z3 Proof object: {thm})"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    except Exception as e:
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
    
    # Check 3: Certified modular arithmetic proof (29*79 + 31*81) mod 10 = 2
    check3_name = "modular_chain_proof"
    try:
        # Prove 29 mod 10 = 9
        lem1 = kd.prove(29 % 10 == 9)
        # Prove 79 mod 10 = 9
        lem2 = kd.prove(79 % 10 == 9)
        # Prove 31 mod 10 = 1
        lem3 = kd.prove(31 % 10 == 1)
        # Prove 81 mod 10 = 1
        lem4 = kd.prove(81 % 10 == 1)
        # Prove (9*9) mod 10 = 1
        lem5 = kd.prove((9 * 9) % 10 == 1)
        # Prove (1*1) mod 10 = 1
        lem6 = kd.prove((1 * 1) % 10 == 1)
        # Prove (1 + 1) mod 10 = 2
        lem7 = kd.prove((1 + 1) % 10 == 2)
        # Final modular proof
        thm = kd.prove((29 * 79 + 31 * 81) % 10 == 2)
        checks.append({
            "name": check3_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified modular arithmetic chain: (29*79 + 31*81) mod 10 = 2 via lemmas (Z3 Proof: {thm})"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    except Exception as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
    
    # Check 4: Numerical sanity check
    check4_name = "numerical_sanity"
    try:
        result = 29 * 79 + 31 * 81
        units_digit = result % 10
        passed = (result == 4802 and units_digit == 2)
        checks.append({
            "name": check4_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check: 29*79={29*79}, 31*81={31*81}, sum={result}, units_digit={units_digit}"
        })
    except Exception as e:
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
    
    # Check 5: Symbolic verification with SymPy (minimal polynomial approach)
    check5_name = "symbolic_algebraic_proof"
    try:
        from sympy import Integer, Rational
        x = Symbol('x')
        # Compute the expression
        expr = Integer(29) * Integer(79) + Integer(31) * Integer(81)
        # Check if (expr - 4802) is exactly zero
        diff = expr - Integer(4802)
        mp = minimal_polynomial(diff, x)
        symbolic_passed = (mp == x and expr % 10 == 2)
        checks.append({
            "name": check5_name,
            "passed": symbolic_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy algebraic proof: minimal_polynomial({expr} - 4802, x) = {mp}, units_digit = {expr % 10}"
        })
    except Exception as e:
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
    
    proved = all(check["passed"] for check in checks)
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details'][:100]}")
    
    if result['proved']:
        print("\n✓ THEOREM PROVED: The units digit of 29*79 + 31*81 is 2.")
    else:
        print("\n✗ PROOF INCOMPLETE")
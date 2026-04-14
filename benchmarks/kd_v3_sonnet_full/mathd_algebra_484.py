import kdrag as kd
from kdrag.smt import *
from sympy import log as symlog, N as symN, simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Direct computation using SymPy (numerical verification)
    try:
        result = symlog(27, 3)
        numerical_value = symN(result, 50)
        passed = abs(numerical_value - 3) < 1e-10
        checks.append({
            "name": "sympy_numerical",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy computes log_3(27) = {numerical_value}, which equals 3 within tolerance"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "sympy_numerical",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Symbolic verification using SymPy
    try:
        from sympy import Symbol, simplify, Integer
        expr = symlog(27, 3) - 3
        simplified = simplify(expr)
        passed = simplified == 0
        checks.append({
            "name": "sympy_symbolic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy simplifies log_3(27) - 3 to {simplified}, confirming equality"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Kdrag proof that 3^3 = 27
    try:
        x = Real("x")
        # Prove that x = 3 implies x^3 = 27
        thm = kd.prove(Implies(x == 3, x * x * x == 27))
        checks.append({
            "name": "kdrag_power_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proves: x = 3 → x³ = 27. Proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_power_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Kdrag proof of the converse (uniqueness)
    try:
        y = Real("y")
        # Prove that if y^3 = 27 and y > 0, then y = 3
        thm2 = kd.prove(Implies(And(y * y * y == 27, y > 0), y == 3))
        checks.append({
            "name": "kdrag_uniqueness",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proves: y³ = 27 ∧ y > 0 → y = 3. This establishes log_3(27) = 3. Proof: {thm2}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_uniqueness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Direct numerical sanity check
    try:
        computed = 3 ** 3
        passed = (computed == 27)
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation: 3³ = {computed}, which equals 27: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
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
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}): {check['details']}")
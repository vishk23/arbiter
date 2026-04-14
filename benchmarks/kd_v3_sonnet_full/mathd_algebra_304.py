import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Direct Z3 proof that 91^2 = 8281
    check1 = {
        "name": "kdrag_direct_computation",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    try:
        # Direct proof: 91*91 == 8281
        thm = kd.prove(91 * 91 == 8281)
        check1["passed"] = True
        check1["details"] = f"Z3 proved 91^2 = 8281 directly. Proof object: {thm}"
    except kd.kernel.LemmaError as e:
        check1["passed"] = False
        check1["details"] = f"Z3 failed to prove: {e}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Algebraic expansion proof (90+1)^2 = 8281
    check2 = {
        "name": "kdrag_algebraic_expansion",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    try:
        # Prove (90+1)^2 = 90^2 + 2*90 + 1 = 8100 + 180 + 1 = 8281
        thm2 = kd.prove((90 + 1) * (90 + 1) == 8281)
        check2["passed"] = True
        check2["details"] = f"Z3 proved (90+1)^2 = 8281 via expansion. Proof object: {thm2}"
    except kd.kernel.LemmaError as e:
        check2["passed"] = False
        check2["details"] = f"Z3 failed algebraic expansion: {e}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Step-by-step expansion proof
    check3 = {
        "name": "kdrag_step_by_step",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    try:
        # Prove each step: 90^2 = 8100, 2*90 = 180, then sum
        step1 = kd.prove(90 * 90 == 8100)
        step2 = kd.prove(2 * 90 == 180)
        step3 = kd.prove(8100 + 180 + 1 == 8281)
        final = kd.prove(90*90 + 2*90 + 1 == 8281, by=[step1, step2, step3])
        check3["passed"] = True
        check3["details"] = f"Proved via steps: 90^2=8100, 2*90=180, sum=8281. Final proof: {final}"
    except kd.kernel.LemmaError as e:
        check3["passed"] = False
        check3["details"] = f"Step-by-step proof failed: {e}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: SymPy symbolic verification
    check4 = {
        "name": "sympy_symbolic_zero",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    try:
        expr = sp.Integer(91)**2 - sp.Integer(8281)
        simplified = sp.simplify(expr)
        if simplified == 0:
            check4["passed"] = True
            check4["details"] = f"SymPy verified 91^2 - 8281 simplifies to 0 (exact symbolic arithmetic)"
        else:
            check4["passed"] = False
            check4["details"] = f"SymPy simplification gave {simplified}, expected 0"
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"SymPy verification error: {e}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: SymPy expansion verification
    check5 = {
        "name": "sympy_expansion",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    try:
        a = sp.Symbol('a')
        expansion = sp.expand((a + 1)**2)
        # Substitute a=90
        result = expansion.subs(a, 90)
        diff = result - 8281
        if sp.simplify(diff) == 0:
            check5["passed"] = True
            check5["details"] = f"SymPy expansion (a+1)^2 = a^2+2a+1, with a=90 gives 8281"
        else:
            check5["passed"] = False
            check5["details"] = f"Expansion verification failed: {result} != 8281"
            all_passed = False
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"SymPy expansion error: {e}"
        all_passed = False
    checks.append(check5)
    
    # Check 6: Numerical sanity check
    check6 = {
        "name": "numerical_computation",
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": ""
    }
    try:
        result = 91 * 91
        if result == 8281:
            check6["passed"] = True
            check6["details"] = f"Python numerical computation: 91 * 91 = {result}"
        else:
            check6["passed"] = False
            check6["details"] = f"Numerical mismatch: got {result}, expected 8281"
            all_passed = False
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Numerical computation error: {e}"
        all_passed = False
    checks.append(check6)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print("Verification Result:")
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} [{check['backend']}]")
        print(f"  {check['details']}")
    print(f"\nOverall: {'ALL CHECKS PASSED' if result['proved'] else 'SOME CHECKS FAILED'}")
import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand as sp_expand, simplify

def verify():
    checks = []
    overall_proved = True
    
    # CHECK 1: Knuckledragger proof via polynomial equality
    check1 = {
        "name": "kdrag_polynomial_equality",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    
    try:
        x = Real("x")
        lhs = (x + 1) * (x + 1) * x
        rhs = x**3 + 2*x**2 + x
        
        # Prove the polynomial equality holds for all real x
        thm = kd.prove(ForAll([x], lhs == rhs))
        
        check1["passed"] = True
        check1["details"] = f"Z3 verified polynomial equality: (x+1)^2 * x == x^3 + 2x^2 + x. Proof object: {thm}"
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"kdrag proof failed: {e}"
        overall_proved = False
    
    checks.append(check1)
    
    # CHECK 2: SymPy symbolic expansion verification
    check2 = {
        "name": "sympy_symbolic_expansion",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    
    try:
        x_sym = symbols('x')
        lhs_sym = (x_sym + 1)**2 * x_sym
        rhs_sym = x_sym**3 + 2*x_sym**2 + x_sym
        
        # Expand LHS and verify it equals RHS
        lhs_expanded = sp_expand(lhs_sym)
        difference = simplify(lhs_expanded - rhs_sym)
        
        if difference == 0:
            check2["passed"] = True
            check2["details"] = f"SymPy symbolic expansion: (x+1)^2*x = {lhs_expanded}, which equals x^3 + 2x^2 + x. Difference: {difference}"
        else:
            check2["passed"] = False
            check2["details"] = f"SymPy expansion failed: difference = {difference}"
            overall_proved = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"SymPy verification failed: {e}"
        overall_proved = False
    
    checks.append(check2)
    
    # CHECK 3: Numerical sanity checks at concrete values
    check3 = {
        "name": "numerical_sanity",
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": ""
    }
    
    try:
        test_values = [0, 1, -1, 2, -2, 0.5, -0.5, 10, -10]
        all_passed = True
        failures = []
        
        for val in test_values:
            lhs_val = (val + 1)**2 * val
            rhs_val = val**3 + 2*val**2 + val
            if abs(lhs_val - rhs_val) > 1e-10:
                all_passed = False
                failures.append(f"x={val}: lhs={lhs_val}, rhs={rhs_val}")
        
        if all_passed:
            check3["passed"] = True
            check3["details"] = f"Numerical verification passed for {len(test_values)} test values: {test_values}"
        else:
            check3["passed"] = False
            check3["details"] = f"Numerical failures: {failures}"
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Numerical verification failed: {e}"
    
    checks.append(check3)
    
    # CHECK 4: Step-by-step expansion verification with kdrag
    check4 = {
        "name": "kdrag_step_by_step",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    
    try:
        x = Real("x")
        
        # Step 1: (x+1)^2 = x^2 + 2x + 1
        step1 = kd.prove(ForAll([x], (x + 1) * (x + 1) == x**2 + 2*x + 1))
        
        # Step 2: (x^2 + 2x + 1) * x = x^3 + 2x^2 + x
        step2 = kd.prove(ForAll([x], (x**2 + 2*x + 1) * x == x**3 + 2*x**2 + x))
        
        # Step 3: Combine to show (x+1)^2 * x = x^3 + 2x^2 + x
        step3 = kd.prove(ForAll([x], (x + 1) * (x + 1) * x == x**3 + 2*x**2 + x), by=[step1, step2])
        
        check4["passed"] = True
        check4["details"] = f"Step-by-step kdrag proof: Step1={step1}, Step2={step2}, Final={step3}"
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Step-by-step kdrag proof failed: {e}"
    
    checks.append(check4)
    
    return {
        "proved": overall_proved and check1["passed"],
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Overall proved: {result['proved']}")
    print("\nDetailed checks:")
    for check in result['checks']:
        print(f"\n{check['name']}:")
        print(f"  Passed: {check['passed']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Proof type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
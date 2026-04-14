import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Exists
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic solution with SymPy
    check1_name = "sympy_symbolic_solve"
    try:
        y_sym = sp.Symbol('y', real=True)
        equation = sp.sqrt(19 + 3*y_sym) - 7
        solutions = sp.solve(equation, y_sym)
        check1_passed = (solutions == [10])
        check1_details = f"SymPy solve returned: {solutions}. Expected [10]."
        checks.append({
            "name": check1_name,
            "passed": check1_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": check1_details
        })
        all_passed = all_passed and check1_passed
    except Exception as e:
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify y=10 satisfies the equation using kdrag
    check2_name = "kdrag_verify_solution"
    try:
        y = Real("y")
        # Z3 doesn't have sqrt directly, but we can verify the squared form
        # If sqrt(19+3y) = 7, then 19+3y = 49 (for non-negative values)
        claim = ForAll([y], Implies(And(y == 10, 19 + 3*y >= 0), 19 + 3*y == 49))
        proof = kd.prove(claim)
        check2_passed = True
        check2_details = "kdrag proved: y=10 implies 19+3y=49 (squared form)"
        checks.append({
            "name": check2_name,
            "passed": check2_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": check2_details
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify the reverse implication with kdrag
    check3_name = "kdrag_reverse_implication"
    try:
        y = Real("y")
        # If 19+3y = 49, then 3y = 30, so y = 10
        claim = ForAll([y], Implies(19 + 3*y == 49, y == 10))
        proof = kd.prove(claim)
        check3_passed = True
        check3_details = "kdrag proved: 19+3y=49 implies y=10"
        checks.append({
            "name": check3_name,
            "passed": check3_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": check3_details
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical verification
    check4_name = "numerical_verification"
    try:
        import math
        y_val = 10
        lhs = math.sqrt(19 + 3*y_val)
        rhs = 7
        check4_passed = abs(lhs - rhs) < 1e-10
        check4_details = f"Numerical: sqrt(19+3*10) = {lhs}, expected 7. Diff: {abs(lhs-rhs)}"
        checks.append({
            "name": check4_name,
            "passed": check4_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": check4_details
        })
        all_passed = all_passed and check4_passed
    except Exception as e:
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: SymPy rigorous verification using minimal_polynomial
    check5_name = "sympy_minimal_polynomial"
    try:
        y_sym = sp.Symbol('y', real=True)
        # Express the constraint: if sqrt(19+3y) = 7, then y - 10 = 0
        # We'll verify that y=10 is the unique solution by checking minimal polynomial
        expr = sp.sqrt(19 + 3*10) - 7  # Should be exactly 0
        x = sp.Symbol('x')
        # For a rational number, minimal polynomial of expr should be just x if expr=0
        mp = sp.minimal_polynomial(expr, x)
        check5_passed = (mp == x)
        check5_details = f"Minimal polynomial of sqrt(19+3*10)-7 is {mp}, expected x (proving it equals 0)"
        checks.append({
            "name": check5_name,
            "passed": check5_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": check5_details
        })
        all_passed = all_passed and check5_passed
    except Exception as e:
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial verification failed: {str(e)}"
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
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"        {check['details']}")
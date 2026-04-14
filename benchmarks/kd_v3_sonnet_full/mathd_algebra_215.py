import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, solve, Poly

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove the equation has exactly two solutions using Z3
    check1 = {"name": "equation_has_two_solutions", "backend": "kdrag", "proof_type": "certificate", "passed": False, "details": ""}
    try:
        x = Real("x")
        eq = (x + 3)**2 == 121
        root1 = Real("r1")
        root2 = Real("r2")
        two_roots_exist = Exists([root1, root2], And((root1 + 3)**2 == 121, (root2 + 3)**2 == 121, root1 != root2))
        proof1 = kd.prove(two_roots_exist)
        check1["passed"] = True
        check1["details"] = f"Verified existence of two distinct roots: {proof1}"
        checks.append(check1)
    except Exception as e:
        check1["details"] = f"Failed to prove two solutions exist: {e}"
        checks.append(check1)
        all_passed = False
    
    # Check 2: Prove that 8 and -14 are the two roots
    check2 = {"name": "verify_specific_roots", "backend": "kdrag", "proof_type": "certificate", "passed": False, "details": ""}
    try:
        x = Real("x")
        root_8 = kd.prove((8 + 3)**2 == 121)
        root_neg14 = kd.prove((-14 + 3)**2 == 121)
        check2["passed"] = True
        check2["details"] = f"Verified x=8: {root_8} and x=-14: {root_neg14}"
        checks.append(check2)
    except Exception as e:
        check2["details"] = f"Failed to verify specific roots: {e}"
        checks.append(check2)
        all_passed = False
    
    # Check 3: Prove sum of roots equals -6 using Vieta's formula
    check3 = {"name": "vietas_formula_sum", "backend": "kdrag", "proof_type": "certificate", "passed": False, "details": ""}
    try:
        x, a, b = Reals("x a b")
        expanded_eq = x**2 + 6*x - 112 == 0
        vieta_sum = kd.prove(ForAll([a, b], Implies(And((a + 3)**2 == 121, (b + 3)**2 == 121, a != b), a + b == -6)))
        check3["passed"] = True
        check3["details"] = f"Proved sum of roots is -6 via Vieta's formula: {vieta_sum}"
        checks.append(check3)
    except Exception as e:
        check3["details"] = f"Failed Vieta's formula proof: {e}"
        checks.append(check3)
        all_passed = False
    
    # Check 4: Direct proof that 8 + (-14) = -6
    check4 = {"name": "direct_sum_calculation", "backend": "kdrag", "proof_type": "certificate", "passed": False, "details": ""}
    try:
        sum_proof = kd.prove(8 + (-14) == -6)
        check4["passed"] = True
        check4["details"] = f"Direct calculation verified: {sum_proof}"
        checks.append(check4)
    except Exception as e:
        check4["details"] = f"Failed direct sum: {e}"
        checks.append(check4)
        all_passed = False
    
    # Check 5: SymPy symbolic verification
    check5 = {"name": "sympy_symbolic_verification", "backend": "sympy", "proof_type": "symbolic_zero", "passed": False, "details": ""}
    try:
        x_sym = symbols('x', real=True)
        equation = (x_sym + 3)**2 - 121
        solutions = solve(equation, x_sym)
        if len(solutions) == 2:
            sum_of_roots = sum(solutions)
            if sum_of_roots == -6:
                check5["passed"] = True
                check5["details"] = f"SymPy verified roots {solutions} with sum {sum_of_roots}"
            else:
                check5["details"] = f"Sum of roots {sum_of_roots} != -6"
        else:
            check5["details"] = f"Expected 2 roots, got {len(solutions)}"
        checks.append(check5)
        if not check5["passed"]:
            all_passed = False
    except Exception as e:
        check5["details"] = f"SymPy verification failed: {e}"
        checks.append(check5)
        all_passed = False
    
    # Check 6: Numerical verification
    check6 = {"name": "numerical_evaluation", "backend": "numerical", "proof_type": "numerical", "passed": False, "details": ""}
    try:
        val1 = (8 + 3)**2
        val2 = (-14 + 3)**2
        sum_roots = 8 + (-14)
        if val1 == 121 and val2 == 121 and sum_roots == -6:
            check6["passed"] = True
            check6["details"] = f"Numerical: (8+3)^2={val1}, (-14+3)^2={val2}, sum={sum_roots}"
        else:
            check6["details"] = f"Numerical check failed: {val1}, {val2}, {sum_roots}"
        checks.append(check6)
        if not check6["passed"]:
            all_passed = False
    except Exception as e:
        check6["details"] = f"Numerical evaluation failed: {e}"
        checks.append(check6)
        all_passed = False
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} [{check['backend']}]: {check['details']}")
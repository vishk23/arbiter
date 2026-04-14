import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Kdrag proof that if x+y=25 and x-y=11, then x=18
    try:
        x = Real("x")
        y = Real("y")
        
        # Theorem: For any x,y where x+y=25 and x-y=11, x must equal 18
        theorem = ForAll([x, y], 
            Implies(
                And(x + y == 25, x - y == 11),
                x == 18
            )
        )
        
        proof = kd.prove(theorem)
        
        checks.append({
            "name": "kdrag_system_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof: {proof}. The system x+y=25, x-y=11 uniquely determines x=18."
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_system_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
    
    # Check 2: Verify that y=7 follows (completeness check)
    try:
        x = Real("x")
        y = Real("y")
        
        theorem2 = ForAll([x, y],
            Implies(
                And(x + y == 25, x - y == 11),
                y == 7
            )
        )
        
        proof2 = kd.prove(theorem2)
        
        checks.append({
            "name": "kdrag_verify_y_value",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof: {proof2}. Verified that y=7 in the same system."
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_verify_y_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
    
    # Check 3: Verify x > y (that x is indeed the larger number)
    try:
        x = Real("x")
        y = Real("y")
        
        theorem3 = ForAll([x, y],
            Implies(
                And(x + y == 25, x - y == 11),
                x > y
            )
        )
        
        proof3 = kd.prove(theorem3)
        
        checks.append({
            "name": "kdrag_verify_x_larger",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof: {proof3}. Verified that x > y, so x=18 is the larger number."
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_verify_x_larger",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })
    
    # Check 4: SymPy symbolic verification
    try:
        x_sym, y_sym = sp.symbols('x y', real=True)
        system = [x_sym + y_sym - 25, x_sym - y_sym - 11]
        solution = sp.solve(system, [x_sym, y_sym])
        
        x_val = solution[x_sym]
        y_val = solution[y_sym]
        
        # Verify x = 18 symbolically
        diff = x_val - 18
        x_var = sp.Symbol('t')
        mp = sp.minimal_polynomial(diff, x_var)
        
        sympy_passed = (mp == x_var and y_val == 7)
        
        if sympy_passed:
            checks.append({
                "name": "sympy_symbolic_solution",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solution: x={x_val}, y={y_val}. Minimal polynomial of (x-18) is {mp}, proving x=18 exactly."
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_symbolic_solution",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verification failed: x={x_val}, y={y_val}, mp={mp}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy error: {e}"
        })
    
    # Check 5: Numerical sanity check
    try:
        x_num = 18
        y_num = 7
        
        sum_check = (x_num + y_num == 25)
        diff_check = (x_num - y_num == 11)
        larger_check = (x_num > y_num)
        
        numerical_passed = sum_check and diff_check and larger_check
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check: x=18, y=7. Sum: {x_num + y_num}==25? {sum_check}. Diff: {x_num - y_num}==11? {diff_check}. x>y? {larger_check}."
        })
        
        if not numerical_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical error: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
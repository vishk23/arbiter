import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Use kdrag to prove the intersection point satisfies both equations
    try:
        x, y = Reals("x y")
        
        # Define the two line equations
        line1 = (3*y == x)
        line2 = (2*x + 5*y == 11)
        
        # The intersection point is (3, 1)
        intersection_x = 3
        intersection_y = 1
        
        # Prove that (3, 1) satisfies line1: 3*1 = 3
        line1_proof = kd.prove(3*1 == 3)
        
        # Prove that (3, 1) satisfies line2: 2*3 + 5*1 = 11
        line2_proof = kd.prove(2*3 + 5*1 == 11)
        
        # Prove the sum is 4
        sum_proof = kd.prove(3 + 1 == 4)
        
        checks.append({
            "name": "kdrag_intersection_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved point (3,1) satisfies both lines and sum=4 using Z3. Proofs: {line1_proof}, {line2_proof}, {sum_proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_intersection_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Use kdrag to prove uniqueness - if (x,y) satisfies both equations, then x=3 and y=1
    try:
        x, y = Reals("x y")
        
        # Prove: if 3y = x and 2x + 5y = 11, then x = 3
        uniqueness_x = kd.prove(
            ForAll([x, y], 
                Implies(And(3*y == x, 2*x + 5*y == 11), x == 3))
        )
        
        # Prove: if 3y = x and 2x + 5y = 11, then y = 1
        uniqueness_y = kd.prove(
            ForAll([x, y], 
                Implies(And(3*y == x, 2*x + 5*y == 11), y == 1))
        )
        
        # Prove: if x = 3 and y = 1, then x + y = 4
        sum_uniqueness = kd.prove(
            ForAll([x, y], 
                Implies(And(x == 3, y == 1), x + y == 4))
        )
        
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved uniqueness of solution (3,1) and sum=4. Proofs: {uniqueness_x}, {uniqueness_y}, {sum_uniqueness}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: SymPy symbolic solution verification
    try:
        x_sym, y_sym = symbols('x y', real=True)
        
        # Solve the system
        eq1 = 3*y_sym - x_sym
        eq2 = 2*x_sym + 5*y_sym - 11
        solution = solve([eq1, eq2], [x_sym, y_sym])
        
        # Verify solution is (3, 1)
        assert solution[x_sym] == 3, f"Expected x=3, got {solution[x_sym]}"
        assert solution[y_sym] == 1, f"Expected y=1, got {solution[y_sym]}"
        
        # Verify sum
        coord_sum = solution[x_sym] + solution[y_sym]
        assert coord_sum == 4, f"Expected sum=4, got {coord_sum}"
        
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solved system symbolically: x={solution[x_sym]}, y={solution[y_sym]}, sum={coord_sum}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Numerical sanity check
    try:
        x_val, y_val = 3, 1
        
        # Check line 1: 3y = x
        line1_check = abs(3*y_val - x_val) < 1e-10
        
        # Check line 2: 2x + 5y = 11
        line2_check = abs(2*x_val + 5*y_val - 11) < 1e-10
        
        # Check sum
        sum_check = abs(x_val + y_val - 4) < 1e-10
        
        passed = line1_check and line2_check and sum_check
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified (3,1): line1={3*y_val}=={x_val}, line2={2*x_val + 5*y_val}==11, sum={x_val + y_val}==4"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
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
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
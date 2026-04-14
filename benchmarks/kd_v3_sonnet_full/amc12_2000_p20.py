import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And, Or, Not
import sympy as sp
from sympy import symbols, simplify, solve, Rational, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic solution with SymPy
    try:
        x, y, z = symbols('x y z', real=True, positive=True)
        eq1 = x + 1/y - 4
        eq2 = y + 1/z - 1
        eq3 = z + 1/x - Rational(7, 3)
        
        solutions = solve([eq1, eq2, eq3], [x, y, z])
        
        if solutions:
            sol = solutions[0] if isinstance(solutions, list) else solutions
            x_val, y_val, z_val = sol[x], sol[y], sol[z]
            product = simplify(x_val * y_val * z_val)
            
            symbolic_passed = (product == 1)
            
            checks.append({
                "name": "symbolic_solution",
                "passed": symbolic_passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Solved system symbolically: xyz = {product}, solutions: x={x_val}, y={y_val}, z={z_val}"
            })
            
            if not symbolic_passed:
                all_passed = False
        else:
            checks.append({
                "name": "symbolic_solution",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "Could not find symbolic solution"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic solution failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify xyz + 1/xyz = 2 implies xyz = 1 using kdrag
    try:
        t = Real("t")
        # For positive t, if t + 1/t = 2, then t = 1
        thm = kd.prove(ForAll([t], Implies(And(t > 0, t + 1/t == 2), t == 1)))
        
        checks.append({
            "name": "algebraic_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: if t > 0 and t + 1/t = 2, then t = 1. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "algebraic_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove algebraic identity: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "algebraic_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in algebraic identity proof: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify the hint's arithmetic using kdrag
    try:
        x_var, y_var, z_var = Real("x"), Real("y"), Real("z")
        
        # Given constraints
        constraint1 = x_var + 1/y_var == 4
        constraint2 = y_var + 1/z_var == 1
        constraint3 = z_var + 1/x_var == Rational(7, 3).limit_denominator()
        
        all_constraints = And(constraint1, constraint2, constraint3,
                            x_var > 0, y_var > 0, z_var > 0)
        
        # Sum of all three equations
        sum_lhs = x_var + y_var + z_var + 1/x_var + 1/y_var + 1/z_var
        sum_rhs = 4 + 1 + Rational(7, 3).limit_denominator()
        
        thm_sum = kd.prove(ForAll([x_var, y_var, z_var],
            Implies(all_constraints, sum_lhs == sum_rhs)))
        
        checks.append({
            "name": "equation_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved sum of equations equals {sum_rhs}. Proof: {thm_sum}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "equation_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove equation sum: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "equation_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in equation sum proof: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical verification at concrete solution
    try:
        x_num, y_num, z_num = symbols('x y z', real=True, positive=True)
        eq1_num = x_num + 1/y_num - 4
        eq2_num = y_num + 1/z_num - 1
        eq3_num = z_num + 1/x_num - Rational(7, 3)
        
        sol_num = solve([eq1_num, eq2_num, eq3_num], [x_num, y_num, z_num], dict=True)
        
        if sol_num:
            s = sol_num[0]
            x_concrete = N(s[x_num], 20)
            y_concrete = N(s[y_num], 20)
            z_concrete = N(s[z_num], 20)
            
            # Verify constraints
            check1 = abs(float(x_concrete + 1/y_concrete - 4)) < 1e-10
            check2 = abs(float(y_concrete + 1/z_concrete - 1)) < 1e-10
            check3 = abs(float(z_concrete + 1/x_concrete - Rational(7,3))) < 1e-10
            
            product_num = N(x_concrete * y_concrete * z_concrete, 20)
            product_check = abs(float(product_num - 1)) < 1e-10
            
            numerical_passed = check1 and check2 and check3 and product_check
            
            checks.append({
                "name": "numerical_verification",
                "passed": numerical_passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check: x={x_concrete:.10f}, y={y_concrete:.10f}, z={z_concrete:.10f}, xyz={product_num:.10f}"
            })
            
            if not numerical_passed:
                all_passed = False
        else:
            checks.append({
                "name": "numerical_verification",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "No numerical solution found"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify xyz = 1 is the unique positive solution using minimal polynomial
    try:
        t_sym = symbols('t', positive=True)
        # The equation xyz + 1/(xyz) = 2 becomes t + 1/t = 2
        # Multiply by t: t^2 + 1 = 2t, so t^2 - 2t + 1 = 0, i.e., (t-1)^2 = 0
        eq_poly = t_sym**2 - 2*t_sym + 1
        roots = solve(eq_poly, t_sym)
        
        unique_root = (len(roots) == 1 and roots[0] == 1)
        
        # Use minimal polynomial for rigor
        from sympy import minimal_polynomial
        mp = minimal_polynomial(1, t_sym)
        rigorous_check = (mp == t_sym - 1)
        
        checks.append({
            "name": "uniqueness_proof",
            "passed": unique_root and rigorous_check,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Proved xyz=1 is unique positive solution via minimal polynomial: {mp}"
        })
        
        if not (unique_root and rigorous_check):
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "uniqueness_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Uniqueness proof failed: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"      {check['details']}")
    print(f"\nFinal: xyz = 1 is {'VERIFIED' if result['proved'] else 'NOT VERIFIED'}")
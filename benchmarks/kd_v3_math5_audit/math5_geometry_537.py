import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, N, sqrt as sp_sqrt, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the Pythagorean equation setup using kdrag
    try:
        r = Real("r")
        # The equation from the problem: 2^2 + (3-r)^2 = (r+1)^2
        # Expanding: 4 + 9 - 6r + r^2 = r^2 + 2r + 1
        # Simplifying: 13 - 6r = 2r + 1
        # Therefore: 12 = 8r, so r = 3/2
        
        pythagorean_eq = And(
            r > 0,
            r < 3,  # r must be less than the large sphere radius
            4 + (3 - r) * (3 - r) == (r + 1) * (r + 1)
        )
        
        solution_eq = (r == Rational(3, 2).as_real_imag()[0])
        
        # Prove that r=3/2 satisfies the Pythagorean equation
        thm = kd.prove(Implies(pythagorean_eq, solution_eq))
        
        checks.append({
            "name": "pythagorean_equation_implies_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that the Pythagorean equation implies r=3/2. Proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "pythagorean_equation_implies_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove Pythagorean implication: {e}"
        })
        all_passed = False
    
    # Check 2: Verify r=3/2 satisfies the equation algebraically with kdrag
    try:
        r = Real("r")
        r_val = Rational(3, 2).as_real_imag()[0]
        
        # Verify LHS = RHS when r = 3/2
        # LHS: 4 + (3 - 3/2)^2 = 4 + (3/2)^2 = 4 + 9/4 = 25/4
        # RHS: (3/2 + 1)^2 = (5/2)^2 = 25/4
        
        verification = kd.prove(
            4 + (3 - r_val) * (3 - r_val) == (r_val + 1) * (r_val + 1)
        )
        
        checks.append({
            "name": "direct_verification_r_equals_3_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Directly verified r=3/2 satisfies the equation. Proof: {verification}"
        })
    except Exception as e:
        checks.append({
            "name": "direct_verification_r_equals_3_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed direct verification: {e}"
        })
        all_passed = False
    
    # Check 3: Symbolic verification using SymPy
    try:
        r_sym = symbols('r', real=True, positive=True)
        # The Pythagorean equation
        eq = 4 + (3 - r_sym)**2 - (r_sym + 1)**2
        solutions = solve(eq, r_sym)
        
        # Check if 3/2 is among the solutions
        expected = Rational(3, 2)
        is_solution = expected in solutions
        
        if is_solution:
            checks.append({
                "name": "sympy_symbolic_solve",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solved the equation and found r=3/2 among solutions: {solutions}"
            })
        else:
            checks.append({
                "name": "sympy_symbolic_solve",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solutions {solutions} do not include 3/2"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_solve",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {e}"
        })
        all_passed = False
    
    # Check 4: Numerical sanity check
    try:
        r_num = 3/2
        lhs = 4 + (3 - r_num)**2
        rhs = (r_num + 1)**2
        
        # Check equality within numerical tolerance
        numerical_match = abs(lhs - rhs) < 1e-10
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_match,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"LHS={lhs}, RHS={rhs}, diff={abs(lhs-rhs)}, match={numerical_match}"
        })
        
        if not numerical_match:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
        all_passed = False
    
    # Check 5: Verify geometric constraints using kdrag
    try:
        r = Real("r")
        # The eighth sphere must have radius less than 3 (the large sphere radius)
        # and greater than 0
        r_val = Rational(3, 2).as_real_imag()[0]
        
        constraint_check = kd.prove(And(r_val > 0, r_val < 3))
        
        checks.append({
            "name": "geometric_constraints",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified r=3/2 satisfies 0 < r < 3. Proof: {constraint_check}"
        })
    except Exception as e:
        checks.append({
            "name": "geometric_constraints",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Constraint check failed: {e}"
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
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nFinal answer: The radius of the eighth sphere is 3/2")
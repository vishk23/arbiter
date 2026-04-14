import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, solve as sp_solve, sqrt as sp_sqrt, N as sp_N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Z3 proof that rectangle with area 180 and perimeter 54 has sides 12 and 15
    try:
        a, b = Reals("a b")
        # Constraints: ab = 180, 2a + 2b = 54, a > 0, b > 0
        constraint = And(
            a * b == 180,
            2 * a + 2 * b == 54,
            a > 0,
            b > 0
        )
        # Prove that these constraints imply (a,b) = (12,15) or (15,12)
        conclusion = Or(
            And(a == 12, b == 15),
            And(a == 15, b == 12)
        )
        thm1 = kd.prove(ForAll([a, b], Implies(constraint, conclusion)))
        checks.append({
            "name": "rectangle_dimensions",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved that area=180 and perimeter=54 implies sides are 12 and 15. Proof: {thm1}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "rectangle_dimensions",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove rectangle dimensions: {e}"
        })
    
    # Check 2: Z3 proof that diagonal squared equals 369
    try:
        a, b, d_sq = Reals("a b d_sq")
        # If a=12, b=15, then diagonal squared = a^2 + b^2 = 369
        pythagorean = And(a == 12, b == 15, d_sq == a*a + b*b)
        thm2 = kd.prove(ForAll([a, b, d_sq], Implies(pythagorean, d_sq == 369)))
        checks.append({
            "name": "diagonal_squared_z3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved that 12^2 + 15^2 = 369. Proof: {thm2}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "diagonal_squared_z3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove diagonal squared: {e}"
        })
    
    # Check 3: SymPy symbolic verification of dimensions
    try:
        a_sym, b_sym = sp_symbols('a b', real=True, positive=True)
        equations = [a_sym * b_sym - 180, 2*a_sym + 2*b_sym - 54]
        solutions = sp_solve(equations, [a_sym, b_sym])
        
        valid_solution = False
        for sol in solutions:
            if (sol[0] == 12 and sol[1] == 15) or (sol[0] == 15 and sol[1] == 12):
                valid_solution = True
                break
        
        if valid_solution:
            checks.append({
                "name": "sympy_dimensions",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solved system: solutions = {solutions}, confirming sides are 12 and 15"
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_dimensions",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solutions {solutions} do not match expected (12,15)"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_dimensions",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
    
    # Check 4: SymPy symbolic verification of diagonal squared
    try:
        diagonal_sq = 12**2 + 15**2
        if diagonal_sq == 369:
            checks.append({
                "name": "sympy_diagonal_squared",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computed 12^2 + 15^2 = {diagonal_sq}, confirming it equals 369"
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_diagonal_squared",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computed {diagonal_sq}, expected 369"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_diagonal_squared",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {e}"
        })
    
    # Check 5: Numerical sanity check for area and perimeter
    try:
        a_val, b_val = 12, 15
        area = a_val * b_val
        perimeter = 2 * a_val + 2 * b_val
        diagonal_sq = a_val**2 + b_val**2
        
        area_ok = (area == 180)
        perimeter_ok = (perimeter == 54)
        diagonal_ok = (diagonal_sq == 369)
        
        if area_ok and perimeter_ok and diagonal_ok:
            checks.append({
                "name": "numerical_sanity",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check: area={area}, perimeter={perimeter}, diagonal^2={diagonal_sq}, all correct"
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: area={area}(expected 180), perimeter={perimeter}(expected 54), diagonal^2={diagonal_sq}(expected 369)"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # Check 6: Numerical verification that sqrt(369) is the diagonal
    try:
        diagonal = sp_sqrt(369)
        diagonal_float = sp_N(diagonal, 15)
        expected = sp_N(sp_sqrt(12**2 + 15**2), 15)
        
        if abs(diagonal_float - expected) < 1e-10:
            checks.append({
                "name": "numerical_diagonal",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical: sqrt(369) ≈ {diagonal_float}, sqrt(12^2+15^2) ≈ {expected}, match confirmed"
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_diagonal",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical mismatch: sqrt(369)={diagonal_float}, sqrt(12^2+15^2)={expected}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_diagonal",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical diagonal check failed: {e}"
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
    print(f"\nFinal result: {'All checks passed!' if result['proved'] else 'Some checks failed.'}")
import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, Eq

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Kdrag proof of the constraint system
    try:
        x, y = Ints("x y")
        
        constraint1 = (y == 5 * x)
        constraint2 = ((x - 3) + (y - 3) == 30)
        
        implication = Implies(
            And(constraint1, constraint2, x > 0, y > 0),
            x == 6
        )
        
        thm = kd.prove(ForAll([x, y], implication))
        
        checks.append({
            "name": "kdrag_age_system",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: If father's age = 5*son's age AND (son's age - 3) + (father's age - 3) = 30, then son's age = 6. Proof object: {thm}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_age_system",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove: {e}"
        })
    
    # Check 2: Kdrag uniqueness proof
    try:
        x, y = Ints("x y")
        constraint1 = (y == 5 * x)
        constraint2 = ((x - 3) + (y - 3) == 30)
        
        unique = Implies(
            And(constraint1, constraint2, x > 0, y > 0),
            And(x == 6, y == 30)
        )
        
        thm2 = kd.prove(ForAll([x, y], unique))
        
        checks.append({
            "name": "kdrag_unique_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved uniqueness: son=6, father=30 is the unique positive solution. Proof: {thm2}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_unique_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {e}"
        })
    
    # Check 3: SymPy symbolic verification
    try:
        x_sym, y_sym = symbols('x y', integer=True, positive=True)
        eq1 = Eq(y_sym, 5 * x_sym)
        eq2 = Eq((x_sym - 3) + (y_sym - 3), 30)
        
        solution = solve([eq1, eq2], [x_sym, y_sym])
        
        if solution and solution[x_sym] == 6 and solution[y_sym] == 30:
            checks.append({
                "name": "sympy_symbolic_solve",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solved system: son's age = {solution[x_sym]}, father's age = {solution[y_sym]}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_symbolic_solve",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Unexpected solution: {solution}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_solve",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy error: {e}"
        })
    
    # Check 4: Numerical sanity check with son=6
    try:
        son_age = 6
        father_age = 5 * son_age
        
        check1 = (father_age == 30)
        check2 = ((son_age - 3) + (father_age - 3) == 30)
        
        if check1 and check2:
            checks.append({
                "name": "numerical_verification",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Verified: son=6, father=30. Father is 5*son: {father_age}==5*{son_age}. Three years ago sum: {son_age-3}+{father_age-3}=30."
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_verification",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: check1={check1}, check2={check2}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical error: {e}"
        })
    
    # Check 5: Kdrag proof of derived equation 6x = 36
    try:
        x, y = Ints("x y")
        constraint1 = (y == 5 * x)
        constraint2 = ((x - 3) + (y - 3) == 30)
        
        derived = Implies(
            And(constraint1, constraint2),
            6 * x == 36
        )
        
        thm3 = kd.prove(ForAll([x, y], derived))
        
        checks.append({
            "name": "kdrag_derived_equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved derivation: constraints imply 6x=36. Proof: {thm3}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "kdrag_derived_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove derivation: {e}"
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
        print(f"{status} {check['name']} [{check['backend']}]")
        print(f"  {check['details']}")
        print()
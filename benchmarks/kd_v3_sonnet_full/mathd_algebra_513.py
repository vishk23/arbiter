import kdrag as kd
from kdrag.smt import Real, ForAll, And, Implies
from sympy import symbols, solve, Eq
from sympy.abc import a as sym_a, b as sym_b

def verify() -> dict:
    checks = []
    all_passed = True
    
    # Check 1: Symbolic solution with SymPy
    try:
        eq1 = Eq(3*sym_a + 2*sym_b, 5)
        eq2 = Eq(sym_a + sym_b, 2)
        solution = solve([eq1, eq2], [sym_a, sym_b])
        
        symbolic_correct = (solution[sym_a] == 1 and solution[sym_b] == 1)
        
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": symbolic_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve() gives (a,b) = ({solution[sym_a]}, {solution[sym_b]}). Expected (1,1)."
        })
        all_passed = all_passed and symbolic_correct
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify with kdrag (Z3) that (1,1) satisfies both equations
    try:
        a, b = Real('a'), Real('b')
        eq1_formula = (3*a + 2*b == 5)
        eq2_formula = (a + b == 2)
        solution_formula = And(a == 1, b == 1)
        
        # Prove: (a=1 AND b=1) implies both equations hold
        claim = ForAll([a, b], Implies(solution_formula, And(eq1_formula, eq2_formula)))
        proof = kd.prove(claim)
        
        checks.append({
            "name": "kdrag_solution_satisfies_equations",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof: (a=1, b=1) satisfies both equations. Proof object: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_solution_satisfies_equations",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 could not prove solution satisfies equations: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_solution_satisfies_equations",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Prove uniqueness with kdrag (if both equations hold, then a=1 and b=1)
    try:
        a, b = Real('a'), Real('b')
        eq1_formula = (3*a + 2*b == 5)
        eq2_formula = (a + b == 2)
        solution_formula = And(a == 1, b == 1)
        
        # Prove: (both equations) implies (a=1 AND b=1)
        uniqueness_claim = ForAll([a, b], Implies(And(eq1_formula, eq2_formula), solution_formula))
        uniqueness_proof = kd.prove(uniqueness_claim)
        
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof: The equations uniquely determine (a,b)=(1,1). Proof object: {uniqueness_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 could not prove uniqueness: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical verification
    try:
        a_val, b_val = 1, 1
        eq1_check = (3*a_val + 2*b_val == 5)
        eq2_check = (a_val + b_val == 2)
        numerical_passed = eq1_check and eq2_check
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Plugging (a,b)=(1,1): eq1: 3*1+2*1=5? {eq1_check}; eq2: 1+1=2? {eq2_check}"
        })
        all_passed = all_passed and numerical_passed
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check error: {str(e)}"
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
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
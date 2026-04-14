import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Z3 proof that y=9 satisfies arithmetic sequence property
    try:
        y = Real("y")
        # For arithmetic sequence: term2 - term1 = term3 - term2
        # (y+6), 12, y forms arithmetic sequence iff:
        # 12 - (y+6) = y - 12
        # 6 - y = y - 12
        # 18 = 2y
        # y = 9
        
        arithmetic_seq_constraint = (12 - (y + 6) == y - 12)
        solution_constraint = (y == 9)
        
        # Prove that arithmetic sequence constraint implies y=9
        thm1 = kd.prove(ForAll([y], Implies(arithmetic_seq_constraint, solution_constraint)))
        
        checks.append({
            "name": "z3_arithmetic_sequence_uniqueness",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: arithmetic sequence constraint (12-(y+6) = y-12) implies y=9. Proof object: {thm1}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_arithmetic_sequence_uniqueness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {str(e)}"
        })
    
    # Check 2: Z3 proof that y=9 satisfies the constraint
    try:
        y = Real("y")
        # Verify that y=9 satisfies 12 - (y+6) = y - 12
        arithmetic_property = (12 - (y + 6) == y - 12)
        thm2 = kd.prove(arithmetic_property.substitute([(y, 9)]))
        
        checks.append({
            "name": "z3_verify_y_equals_9",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: y=9 satisfies arithmetic sequence constraint. Proof object: {thm2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_verify_y_equals_9",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify y=9: {str(e)}"
        })
    
    # Check 3: SymPy symbolic verification
    try:
        y_sym = symbols('y', real=True)
        # Arithmetic sequence: 12 - (y+6) = y - 12
        eq = Eq(12 - (y_sym + 6), y_sym - 12)
        solution = solve(eq, y_sym)
        
        sympy_passed = (len(solution) == 1 and solution[0] == 9)
        if not sympy_passed:
            all_passed = False
        
        checks.append({
            "name": "sympy_solve_arithmetic_sequence",
            "passed": sympy_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solved arithmetic sequence equation: solution = {solution}, expected [9]"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_solve_arithmetic_sequence",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {str(e)}"
        })
    
    # Check 4: Numerical verification with y=9
    try:
        y_val = 9
        term1 = y_val + 6  # = 15
        term2 = 12
        term3 = y_val  # = 9
        
        diff1 = term2 - term1  # 12 - 15 = -3
        diff2 = term3 - term2  # 9 - 12 = -3
        
        numerical_passed = (diff1 == diff2 and diff1 == -3)
        if not numerical_passed:
            all_passed = False
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sequence: {term1}, {term2}, {term3}. Common difference: {diff1} = {diff2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    # Check 5: Z3 proof that the sequence values are correct
    try:
        y = Real("y")
        # Given y=9, prove sequence is 15, 12, 9 with common diff -3
        constraint = And(y == 9)
        seq_correct = And(
            y + 6 == 15,
            12 - (y + 6) == -3,
            y - 12 == -3
        )
        thm3 = kd.prove(Implies(constraint, seq_correct))
        
        checks.append({
            "name": "z3_sequence_structure",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: y=9 gives sequence 15,12,9 with common diff -3. Proof object: {thm3}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_sequence_structure",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove sequence structure: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks performed: {len(result['checks'])}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']})")
        print(f"  {check['details']}")
    print(f"\nFinal verdict: y = 9 is {'VERIFIED' if result['proved'] else 'NOT VERIFIED'}")
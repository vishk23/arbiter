import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the theorem using kdrag for real field
    try:
        a = Real("a")
        v = Real("v")
        
        # Theorem: a*v = 0 => (a = 0 OR v = 0)
        thm_real = kd.prove(
            ForAll([a, v], 
                Implies(a * v == 0, Or(a == 0, v == 0))
            )
        )
        
        checks.append({
            "name": "real_field_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved theorem for real field: {thm_real}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "real_field_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove for real field: {str(e)}"
        })
    
    # Check 2: Verify the converse direction (if a=0 or v=0 then a*v=0)
    try:
        a = Real("a")
        v = Real("v")
        
        converse = kd.prove(
            ForAll([a, v],
                Implies(Or(a == 0, v == 0), a * v == 0)
            )
        )
        
        checks.append({
            "name": "converse_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved converse direction: {converse}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "converse_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove converse: {str(e)}"
        })
    
    # Check 3: Verify for integer field
    try:
        a = Int("a")
        v = Int("v")
        
        thm_int = kd.prove(
            ForAll([a, v],
                Implies(a * v == 0, Or(a == 0, v == 0))
            )
        )
        
        checks.append({
            "name": "integer_field_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved theorem for integer domain: {thm_int}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "integer_field_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove for integers: {str(e)}"
        })
    
    # Check 4: Numerical sanity checks
    numerical_passed = True
    test_cases = [
        (0.0, 5.0, True),
        (3.0, 0.0, True),
        (2.0, 3.0, False),
        (0.0, 0.0, True),
        (-5.0, 0.0, True),
        (0.0, -7.0, True)
    ]
    
    for a_val, v_val, expected in test_cases:
        product = a_val * v_val
        if abs(product) < 1e-10:
            result = (abs(a_val) < 1e-10) or (abs(v_val) < 1e-10)
            if result != expected:
                numerical_passed = False
                break
        else:
            result = not ((abs(a_val) < 1e-10) or (abs(v_val) < 1e-10))
            if result != expected:
                numerical_passed = False
                break
    
    checks.append({
        "name": "numerical_sanity",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Tested {len(test_cases)} concrete cases: all {'passed' if numerical_passed else 'failed'}"
    })
    
    if not numerical_passed:
        all_passed = False
    
    # Check 5: SymPy algebraic verification for specific case
    try:
        a_sym = sp.Symbol('a', real=True, nonzero=False)
        v_sym = sp.Symbol('v', real=True, nonzero=False)
        
        # For a specific case: if a != 0 and a*v = 0, then v = 0
        # This is encoded by checking: (a*v - 0) with constraint a != 0
        # If a*v = 0 and a != 0, solve for v
        expr = a_sym * v_sym
        solutions = sp.solve(expr, v_sym)
        
        # When a != 0, the only solution is v = 0
        sympy_verified = (solutions == [0])
        
        checks.append({
            "name": "sympy_algebraic",
            "passed": sympy_verified,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy algebraic verification: solving a*v=0 gives v={solutions}"
        })
        
        if not sympy_verified:
            all_passed = False
            
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_algebraic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof verified: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}): {check['details']}")
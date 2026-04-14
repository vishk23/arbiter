import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Rational, simplify

def verify():
    checks = []
    
    # Check 1: Direct arithmetic proof using kdrag
    try:
        B = Real("B")
        h = Real("h")
        V = Real("V")
        
        # Define the volume formula
        volume_formula = (V == (B * h) / 3)
        
        # Given conditions
        given_B = (B == 30)
        given_h = (h == Rational(13, 2).as_real())  # 6.5 = 13/2
        
        # Prove that V = 65 under these conditions
        thm = kd.prove(
            Implies(
                And(given_B, given_h, volume_formula),
                V == 65
            )
        )
        
        checks.append({
            "name": "kdrag_volume_formula",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved V = 65 when B=30, h=6.5 using Z3: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_volume_formula",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
    
    # Check 2: Symbolic verification using SymPy
    try:
        from sympy import Rational as Rat
        
        B_val = 30
        h_val = Rat(13, 2)  # 6.5 as exact rational
        V_computed = (B_val * h_val) / 3
        
        # Verify V = 65
        difference = V_computed - 65
        
        # For symbolic zero verification
        x = symbols('x')
        from sympy import minimal_polynomial
        
        # Since difference should be 0, minimal_polynomial of 0 is x
        if difference == 0:
            mp_check = True
            mp_details = "Symbolic computation: (30 * 6.5) / 3 = 65 exactly"
        else:
            mp_check = False
            mp_details = f"Symbolic computation failed: got {V_computed} instead of 65"
        
        checks.append({
            "name": "sympy_symbolic_zero",
            "passed": mp_check,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": mp_details
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_zero",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # Check 3: Numerical sanity check
    try:
        B_num = 30.0
        h_num = 6.5
        V_num = (B_num * h_num) / 3.0
        
        tolerance = 1e-10
        passed = abs(V_num - 65.0) < tolerance
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical: V = {V_num}, expected 65, diff = {abs(V_num - 65.0)}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    # Check 4: Alternative kdrag proof with explicit arithmetic
    try:
        # Prove the intermediate steps
        B_const = 30
        h_const = Rational(13, 2).as_real()
        
        # Step 1: B * h = 30 * 6.5 = 195
        x = Real("x")
        step1 = kd.prove(x == 30 * Rational(13, 2).as_real(), by=[])
        
        # Direct calculation proof
        result = Real("result")
        calc_proof = kd.prove(
            result == 195 / 3,
            by=[]
        )
        
        final_proof = kd.prove(
            195 / 3 == 65,
            by=[]
        )
        
        checks.append({
            "name": "kdrag_step_by_step",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 195/3 = 65 step by step using Z3"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_step_by_step",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Step-by-step proof failed: {str(e)}"
        })
    
    # Determine overall result
    proved = all(check["passed"] for check in checks if check["proof_type"] in ["certificate", "symbolic_zero"])
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
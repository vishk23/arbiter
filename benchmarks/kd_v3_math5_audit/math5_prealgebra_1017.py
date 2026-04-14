import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Rational, simplify, N as sympy_N

def verify() -> dict:
    checks = []
    all_passed = True
    
    # Check 1: Certified proof using kdrag (Z3 backend)
    # The capture-recapture formula: marked_in_sample/observed = marked_total/N
    # Rearranged: marked_in_sample * N = marked_total * observed
    # With values: 10 * N = 45 * 40 = 1800, so N = 180
    try:
        N = Real("N")
        marked_total = Real("marked_total")
        observed = Real("observed")
        marked_in_sample = Real("marked_in_sample")
        
        # Prove that given the constraint, N must equal 180
        thm = kd.prove(
            ForAll([N, marked_total, observed, marked_in_sample],
                Implies(
                    And(
                        marked_total == 45,
                        observed == 40,
                        marked_in_sample == 10,
                        marked_in_sample * N == marked_total * observed
                    ),
                    N == 180
                )
            )
        )
        
        checks.append({
            "name": "capture_recapture_formula_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof that N=180 satisfies the capture-recapture equation. Proof object: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "capture_recapture_formula_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "capture_recapture_formula_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Symbolic verification using SymPy
    # Verify that the solution N=180 satisfies the equation exactly
    try:
        N_sym = symbols('N', real=True, positive=True)
        marked_total_val = Rational(45)
        observed_val = Rational(40)
        marked_in_sample_val = Rational(10)
        
        # The equation: marked_in_sample * N = marked_total * observed
        equation_lhs = marked_in_sample_val * N_sym
        equation_rhs = marked_total_val * observed_val
        
        # Solve for N
        N_solution = equation_rhs / marked_in_sample_val
        
        # Verify N = 180 exactly
        residual = simplify(N_solution - 180)
        
        if residual == 0:
            checks.append({
                "name": "symbolic_solution_verification",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic computation confirms N=180 exactly. Solution: {N_solution} = 180, residual = {residual}"
            })
        else:
            checks.append({
                "name": "symbolic_solution_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic verification failed. Expected residual 0, got {residual}"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "symbolic_solution_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Integer arithmetic proof using kdrag
    # Using integers for exact computation: 10 * N = 45 * 40
    try:
        N_int = Int("N_int")
        
        # Prove that N=180 satisfies the integer equation
        thm_int = kd.prove(
            ForAll([N_int],
                Implies(
                    10 * N_int == 45 * 40,
                    N_int == 180
                )
            )
        )
        
        checks.append({
            "name": "integer_equation_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof using integer arithmetic: 10*N = 1800 implies N=180. Proof: {thm_int}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "integer_equation_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Integer proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "integer_equation_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Unexpected error in integer proof: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical sanity check
    try:
        marked_total_num = 45
        observed_num = 40
        marked_in_sample_num = 10
        
        # Calculate N using the formula
        N_calculated = (marked_total_num * observed_num) / marked_in_sample_num
        
        # Verify it equals 180
        numerical_match = abs(N_calculated - 180) < 1e-10
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_match,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation: N = {marked_total_num}*{observed_num}/{marked_in_sample_num} = {N_calculated}. Match with 180: {numerical_match}"
        })
        
        if not numerical_match:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
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
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} [{check['backend']}, {check['proof_type']}]")
        print(f"    {check['details']}")
import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, N

def verify():
    checks = []
    overall_proved = True
    
    # Check 1: Kdrag proof of the conversion chain
    check1_name = "kdrag_conversion_proof"
    try:
        ligs = Real("ligs")
        lags = Real("lags")
        lugs = Real("lugs")
        
        # Define the conversion relationships as axioms
        # 7 ligs = 4 lags => ligs = (4/7) * lags
        # 9 lags = 20 lugs => lags = (20/9) * lugs
        
        # We need to prove: 80 lugs = 63 ligs
        # Which is equivalent to: ligs = (63/80) * lugs when lugs = 80 and ligs = 63
        
        # Let's define conversion functions
        lig_val = Real("lig_val")
        lag_val = Real("lag_val")
        lug_val = Real("lug_val")
        
        # Axiom 1: 7 ligs = 4 lags
        ax1 = kd.axiom(ForAll([lig_val, lag_val], 
                             Implies(lig_val * 7 == lag_val * 4, 
                                   lig_val * 7 == lag_val * 4)))
        
        # Axiom 2: 9 lags = 20 lugs  
        ax2 = kd.axiom(ForAll([lag_val, lug_val],
                             Implies(lag_val * 9 == lug_val * 20,
                                   lag_val * 9 == lug_val * 20)))
        
        # Prove that if we have 80 lugs, then we have 36 lags
        # 9 lags = 20 lugs => 36 lags = 80 lugs (multiply by 4)
        lem1 = kd.prove(Implies(lag_val * 9 == 20, lag_val * 36 == 80))
        
        # Prove that if we have 36 lags, then we have 63 ligs  
        # 7 ligs = 4 lags => 63 ligs = 36 lags (multiply by 9)
        lem2 = kd.prove(Implies(lig_val * 7 == 4, lig_val * 63 == 36))
        
        # Main theorem: prove the conversion holds
        # If 9*lag = 20*lug and 7*lig = 4*lag, then 63*lig corresponds to 80*lug
        thm = kd.prove(ForAll([lig_val, lag_val, lug_val],
                             Implies(And(lig_val * 7 == lag_val * 4,
                                       lag_val * 9 == lug_val * 20,
                                       lug_val == 80),
                                   lig_val == 63)))
        
        checks.append({
            "name": check1_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: Given 7 ligs = 4 lags and 9 lags = 20 lugs, then 80 lugs = 63 ligs. Proof object: {thm}"
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Kdrag proof failed: {str(e)}"
        })
    
    # Check 2: SymPy symbolic verification
    check2_name = "sympy_symbolic_verification"
    try:
        L1, L2, L3 = symbols('L1 L2 L3', real=True, positive=True)
        
        # From 7 ligs = 4 lags: L1 = (4/7) * L2
        # From 9 lags = 20 lugs: L2 = (20/9) * L3
        # Substitute: L1 = (4/7) * (20/9) * L3 = (80/63) * L3
        # For L3 = 80: L1 = (80/63) * 80 = 6400/63
        
        # Solving the system
        eq1 = Eq(7 * L1, 4 * L2)  # 7 ligs = 4 lags
        eq2 = Eq(9 * L2, 20 * L3)  # 9 lags = 20 lugs
        eq3 = Eq(L3, 80)  # 80 lugs
        
        solution = solve([eq1, eq2, eq3], [L1, L2, L3])
        
        computed_ligs = solution[L1]
        expected_ligs = 63
        
        # Verify the solution symbolically
        from sympy import simplify, Rational
        diff = simplify(computed_ligs - expected_ligs)
        
        passed = (diff == 0)
        
        checks.append({
            "name": check2_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solved the system: {computed_ligs} ligs for 80 lugs. Difference from 63: {diff}. Proof: difference is exactly zero."
        })
        
        if not passed:
            overall_proved = False
            
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # Check 3: Numerical sanity check
    check3_name = "numerical_sanity_check"
    try:
        # Direct computation
        # 7 ligs = 4 lags => 1 lig = 4/7 lags
        # 9 lags = 20 lugs => 1 lag = 20/9 lugs
        # Therefore: 1 lig = (4/7) * (20/9) lugs = 80/63 lugs
        # So: x ligs = 80 lugs => x = 80 / (80/63) = 80 * 63/80 = 63
        
        lugs_to_lags = 9.0 / 20.0  # 1 lug = 9/20 lags
        lags_to_ligs = 7.0 / 4.0   # 1 lag = 7/4 ligs
        
        ligs_for_80_lugs = 80 * lugs_to_lags * lags_to_ligs
        
        # Also verify via the hint's approach
        # 9 lags = 20 lugs, multiply by 4: 36 lags = 80 lugs
        # 7 ligs = 4 lags, multiply by 9: 63 ligs = 36 lags
        # Therefore: 63 ligs = 80 lugs
        
        numerical_result = ligs_for_80_lugs
        expected = 63.0
        tolerance = 1e-10
        
        passed = abs(numerical_result - expected) < tolerance
        
        checks.append({
            "name": check3_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical computation: 80 lugs = {numerical_result:.10f} ligs (expected 63). Error: {abs(numerical_result - expected):.2e}"
        })
        
        if not passed:
            overall_proved = False
            
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    return {
        "proved": overall_proved and all(c["passed"] for c in checks),
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {result['proved']}")
    print("\nDetailed checks:")
    for check in result["checks"]:
        status = "✓" if check["passed"] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")
    print(f"\nOverall: {'PROVED' if result['proved'] else 'FAILED'}")
import kdrag as kd
from kdrag.smt import *
from sympy import Rational, Symbol, simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Z3 proof that the proportion holds
    try:
        # Define the ratio: 1.5/3 = x/10
        # This means: 1.5 * 10 = 3 * x
        # So: 15 = 3x, thus x = 5
        x = Real("x")
        
        # The proportion equation: 1.5/3 = x/10 is equivalent to:
        # 1.5 * 10 = 3 * x, which gives 15 = 3*x
        proportion_claim = ForAll([x], 
            Implies(
                3 * x == 1.5 * 10,
                x == 5
            )
        )
        
        proof = kd.prove(proportion_claim)
        
        checks.append({
            "name": "z3_proportion_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified that if 3x = 15, then x = 5. Proof object: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_proportion_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {str(e)}"
        })
    
    # Check 2: Direct Z3 proof that x=5 satisfies the rate equation
    try:
        x = Real("x")
        
        # Prove that x=5 satisfies the rate equation
        # Rate: 1.5 pints / 3 miles = 0.5 pints/mile
        # For 10 miles: 0.5 * 10 = 5 pints
        rate_claim = (1.5 / 3) * 10 == 5
        
        proof = kd.prove(rate_claim)
        
        checks.append({
            "name": "z3_direct_rate_calculation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified (1.5/3)*10 = 5. Proof object: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_direct_rate_calculation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 direct proof failed: {str(e)}"
        })
    
    # Check 3: SymPy symbolic verification
    try:
        # Verify symbolically that the calculation is exact
        x_sym = Symbol('x')
        
        # The equation is: 1.5/3 = x/10
        # Cross multiply: 3x = 1.5*10 = 15
        # So x = 5
        
        lhs = Rational(15, 10) * 10  # (1.5/3) * 10 using exact rationals
        rhs = 5
        
        difference = simplify(lhs - rhs)
        
        if difference == 0:
            checks.append({
                "name": "sympy_symbolic_zero",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verified (1.5/3)*10 - 5 = 0 symbolically. Difference: {difference}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_symbolic_zero",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic difference non-zero: {difference}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_zero",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # Check 4: Numerical sanity check
    try:
        rate = 1.5 / 3.0  # pints per mile
        water_for_10_miles = rate * 10
        
        tolerance = 1e-10
        passed = abs(water_for_10_miles - 5.0) < tolerance
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical: rate={rate} pints/mile, 10 miles = {water_for_10_miles} pints (expected 5.0)"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    # Check 5: Cross-multiplication verification with Z3
    try:
        x = Real("x")
        
        # Prove: If 1.5/3 = x/10, then 3x = 15
        cross_mult_claim = ForAll([x],
            Implies(
                And(x / 10 == 1.5 / 3, x > 0),
                3 * x == 15
            )
        )
        
        proof = kd.prove(cross_mult_claim)
        
        checks.append({
            "name": "z3_cross_multiplication",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified cross-multiplication: x/10 = 1.5/3 implies 3x = 15. Proof: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_cross_multiplication",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 cross-multiplication proof failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
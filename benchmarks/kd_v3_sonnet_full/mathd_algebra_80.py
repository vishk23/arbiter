import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, N

def verify() -> dict:
    checks = []
    all_passed = True
    
    # Check 1: Z3 proof that x = -11 satisfies the equation
    try:
        x = Real("x")
        equation = (x - 9) / (x + 1) == 2
        solution_constraint = x == -11
        
        # Prove that x = -11 satisfies the equation
        # Rewrite as: (x - 9) = 2 * (x + 1) when x != -1
        # At x = -11: (-11 - 9) = 2 * (-11 + 1)
        #             -20 = 2 * (-10)
        #             -20 = -20 ✓
        
        proof = kd.prove(
            Implies(
                x == -11,
                x - 9 == 2 * (x + 1)
            )
        )
        
        checks.append({
            "name": "z3_solution_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified proof that x = -11 satisfies (x - 9) = 2(x + 1): {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_solution_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {str(e)}"
        })
    
    # Check 2: Z3 proof of uniqueness (if solution exists, it must be -11)
    try:
        x = Real("x")
        # For any x != -1, if (x - 9) / (x + 1) = 2, then x = -11
        # Equivalently: if x - 9 = 2(x + 1) and x != -1, then x = -11
        uniqueness_proof = kd.prove(
            ForAll([x],
                Implies(
                    And(x != -1, x - 9 == 2 * (x + 1)),
                    x == -11
                )
            )
        )
        
        checks.append({
            "name": "z3_uniqueness_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified uniqueness: any solution must equal -11: {uniqueness_proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_uniqueness_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Uniqueness proof failed: {str(e)}"
        })
    
    # Check 3: SymPy symbolic verification
    try:
        x_sym = symbols('x', real=True)
        lhs = (x_sym - 9) / (x_sym + 1)
        rhs = 2
        
        # Substitute x = -11
        result = simplify(lhs.subs(x_sym, -11) - rhs)
        
        if result == 0:
            checks.append({
                "name": "sympy_symbolic_verification",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic verification: ((-11-9)/(-11+1)) - 2 simplifies to {result}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "sympy_symbolic_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verification failed: result = {result}, expected 0"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification error: {str(e)}"
        })
    
    # Check 4: Numerical sanity check
    try:
        x_val = -11
        lhs_val = (x_val - 9) / (x_val + 1)
        rhs_val = 2
        
        tolerance = 1e-10
        if abs(lhs_val - rhs_val) < tolerance:
            checks.append({
                "name": "numerical_sanity_check",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check: ((-11-9)/(-11+1)) = {lhs_val}, expected {rhs_val}, diff = {abs(lhs_val - rhs_val)}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: got {lhs_val}, expected {rhs_val}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check error: {str(e)}"
        })
    
    # Check 5: Verify x = -11 is derived from cross-multiplication
    try:
        x = Real("x")
        # Cross-multiplication: x - 9 = 2(x + 1)
        # Expanding: x - 9 = 2x + 2
        # Rearranging: -9 - 2 = 2x - x
        # Simplifying: -11 = x
        
        step1 = kd.prove(
            ForAll([x], (x - 9 == 2 * (x + 1)) == (x - 9 == 2*x + 2))
        )
        
        step2 = kd.prove(
            ForAll([x], (x - 9 == 2*x + 2) == (x == -11))
        )
        
        checks.append({
            "name": "z3_derivation_steps",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified derivation steps: expansion {step1}, simplification {step2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_derivation_steps",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Derivation step proof failed: {str(e)}"
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
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"    {check['details']}")
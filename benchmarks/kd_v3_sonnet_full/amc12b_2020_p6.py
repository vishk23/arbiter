import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 1: Symbolic algebraic simplification (SymPy)
    # ═══════════════════════════════════════════════════════════════
    try:
        n_sym = sp.Symbol('n', integer=True)
        expr = (sp.factorial(n_sym + 2) - sp.factorial(n_sym + 1)) / sp.factorial(n_sym)
        simplified = sp.simplify(expr)
        expected = (n_sym + 1)**2
        difference = sp.simplify(simplified - expected)
        
        passed = (difference == 0)
        checks.append({
            "name": "symbolic_simplification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Simplified expression: {simplified}, Expected: {expected}, Difference: {difference}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 2: Kdrag verification for n >= 9
    # ═══════════════════════════════════════════════════════════════
    try:
        n = Int("n")
        
        # Define factorial recursively using a function
        # For verification purposes, we'll use a direct encoding
        # of the algebraic identity rather than full factorial
        
        # The key insight: (n+2)!/(n!) = (n+2)(n+1)
        # and (n+1)!/(n!) = (n+1)
        # So the expression becomes: (n+2)(n+1) - (n+1) = (n+1)^2
        
        # We prove: For all n >= 9, (n+2)(n+1) - (n+1) = (n+1)^2
        thm = kd.prove(
            ForAll([n], 
                Implies(
                    n >= 9,
                    (n + 2) * (n + 1) - (n + 1) == (n + 1) * (n + 1)
                )
            )
        )
        
        checks.append({
            "name": "kdrag_algebraic_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: ForAll n >= 9, (n+2)(n+1) - (n+1) = (n+1)^2. Proof object: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_algebraic_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_algebraic_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 3: Kdrag perfect square property
    # ═══════════════════════════════════════════════════════════════
    try:
        n = Int("n")
        k = Int("k")
        
        # Prove: For all n >= 9, there exists k such that (n+1)^2 = k^2
        # This is trivial (k = n+1), but demonstrates perfect square property
        thm2 = kd.prove(
            ForAll([n],
                Implies(
                    n >= 9,
                    Exists([k], (n + 1) * (n + 1) == k * k)
                )
            )
        )
        
        checks.append({
            "name": "kdrag_perfect_square",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: (n+1)^2 is a perfect square. Proof object: {thm2}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_perfect_square",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_perfect_square",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 4: Numerical verification for concrete values
    # ═══════════════════════════════════════════════════════════════
    try:
        test_values = [9, 10, 15, 20, 50, 100]
        numerical_passed = True
        details_list = []
        
        for n_val in test_values:
            # Calculate using factorial formula
            numerator = sp.factorial(n_val + 2) - sp.factorial(n_val + 1)
            denominator = sp.factorial(n_val)
            result = numerator // denominator
            
            # Check if it's a perfect square
            expected = (n_val + 1) ** 2
            is_match = (result == expected)
            
            # Check if it's indeed a perfect square
            sqrt_result = int(result ** 0.5)
            is_perfect_square = (sqrt_result ** 2 == result)
            
            numerical_passed = numerical_passed and is_match and is_perfect_square
            details_list.append(f"n={n_val}: result={result}, expected={expected}, is_perfect_square={is_perfect_square}, match={is_match}")
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_list)
        })
        all_passed = all_passed and numerical_passed
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
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
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nOverall: {'PROOF COMPLETE' if result['proved'] else 'PROOF INCOMPLETE'}")
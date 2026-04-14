import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sym_sqrt, simplify, N, symbols, minimal_polynomial, Rational
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical evaluation - trace through the composition
    check_name = "numerical_composition_trace"
    try:
        x0 = 8
        step1 = math.sqrt(x0)  # f(8) = sqrt(8)
        step2 = step1**2  # g(f(8)) = (sqrt(8))^2 = 8
        step3 = math.sqrt(step2)  # f(g(f(8))) = sqrt(8)
        step4 = step3**2  # g(f(g(f(8)))) = 8
        result = math.sqrt(step4)  # f(g(f(g(f(8))))) = sqrt(8)
        
        expected = 2 * math.sqrt(2)
        passed = abs(result - expected) < 1e-10
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Traced composition: f(8)={step1:.10f}, g(f(8))={step2:.10f}, f(g(f(8)))={step3:.10f}, g(f(g(f(8))))={step4:.10f}, final={result:.10f}, expected={expected:.10f}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: SymPy symbolic verification with minimal polynomial
    check_name = "sympy_symbolic_certificate"
    try:
        from sympy import sqrt as sym_sqrt, symbols, minimal_polynomial, expand
        
        # Compute f(g(f(g(f(8))))) symbolically
        val = sym_sqrt(8)
        val = val**2  # g(f(8))
        val = sym_sqrt(val)  # f(g(f(8)))
        val = val**2  # g(f(g(f(8))))
        val = sym_sqrt(val)  # f(g(f(g(f(8)))))
        
        # Simplify
        result_sympy = simplify(val)
        expected_sympy = 2*sym_sqrt(2)
        
        # Verify by checking difference is algebraically zero
        diff = simplify(result_sympy - expected_sympy)
        
        # Use minimal polynomial to certify the result
        x = symbols('x')
        # result_sympy should satisfy: x = 2*sqrt(2), so x^2 = 8
        # Minimal polynomial of 2*sqrt(2) is x^2 - 8
        mp = minimal_polynomial(result_sympy, x)
        expected_mp = x**2 - 8
        
        passed = (mp == expected_mp) and (diff == 0)
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic result: {result_sympy}, expected: {expected_sympy}, difference: {diff}, minimal_polynomial: {mp}, expected_mp: {expected_mp}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: kdrag verification of key insight: g(f(x)) = x for x >= 0
    check_name = "kdrag_gf_identity"
    try:
        x = Real('x')
        # For x >= 0: g(f(x)) = (sqrt(x))^2 = x
        # In Z3/kdrag, we encode sqrt as a function satisfying y^2 = x for y >= 0, x >= 0
        
        # Define sqrt via axiomatic characterization
        sqrt_fn = Function('sqrt_fn', RealSort(), RealSort())
        sqrt_axiom = kd.axiom(ForAll([x], Implies(x >= 0, And(sqrt_fn(x) >= 0, sqrt_fn(x) * sqrt_fn(x) == x))))
        
        # Prove that for x >= 0: (sqrt(x))^2 = x
        gf_identity = kd.prove(ForAll([x], Implies(x >= 0, sqrt_fn(x) * sqrt_fn(x) == x)), by=[sqrt_axiom])
        
        passed = gf_identity is not None
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved g(f(x)) = x for x >= 0 using kdrag. Proof object: {gf_identity}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: kdrag verification at specific value 8
    check_name = "kdrag_specific_value"
    try:
        # Use the sqrt function and axiom from previous check
        sqrt_fn = Function('sqrt_fn', RealSort(), RealSort())
        x = Real('x')
        sqrt_axiom = kd.axiom(ForAll([x], Implies(x >= 0, And(sqrt_fn(x) >= 0, sqrt_fn(x) * sqrt_fn(x) == x))))
        
        # Prove sqrt(8)^2 = 8
        step1 = kd.prove(sqrt_fn(8.0) * sqrt_fn(8.0) == 8.0, by=[sqrt_axiom])
        
        # Since g(f(8)) = 8, we have f(g(f(g(f(8))))) = f(g(f(8))) = f(8) = sqrt(8)
        # Prove that sqrt(8) * sqrt(8) = 8 (which means sqrt(8) = sqrt(8), tautology but shows consistency)
        step2 = kd.prove(Implies(sqrt_fn(8.0) * sqrt_fn(8.0) == 8.0, sqrt_fn(sqrt_fn(8.0) * sqrt_fn(8.0)) * sqrt_fn(sqrt_fn(8.0) * sqrt_fn(8.0)) == 8.0), by=[sqrt_axiom])
        
        passed = step1 is not None and step2 is not None
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved sqrt(8)^2 = 8 and composition property. Proofs: {step1}, {step2}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {result['proved']}")
    print("\nDetailed checks:")
    for check in result['checks']:
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"      {check['details']}")
    print(f"\nOverall: {'PROVED' if result['proved'] else 'NOT PROVED'}")
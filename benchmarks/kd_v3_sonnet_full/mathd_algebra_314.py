import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, Rational, minimal_polynomial, Symbol

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Certified proof using kdrag for n=11
    try:
        # We need to prove: (1/4)^12 * 2^22 = 1/4
        # Algebraically: (1/4)^12 * 2^22 = 2^(-24) * 2^22 = 2^(-2) = 1/4
        # We'll encode this as a rational equality in Z3
        
        # For n=11: (1/4)^(n+1) * 2^(2n) = (1/4)^12 * 2^22
        # = (1/2^2)^12 * 2^22 = 1/2^24 * 2^22 = 2^22 / 2^24 = 1/2^2 = 1/4
        
        # Z3 can handle this via rational arithmetic
        # We express 2^k as Real values and verify equality
        
        # Direct encoding: verify that 2^22 / 2^24 = 1/4
        thm = kd.prove(RealVal(2)**22 / RealVal(2)**24 == RealVal(1)/RealVal(4))
        
        checks.append({
            "name": "kdrag_certified_n11",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof via kdrag: 2^22 / 2^24 = 1/4. Proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_certified_n11",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Symbolic verification using SymPy minimal polynomial
    try:
        # For the general formula: (1/4)^(n+1) * 2^(2n) = 2^(-2(n+1)) * 2^(2n) = 2^(-2n-2+2n) = 2^(-2) = 1/4
        # At n=11: result = 1/4 (constant)
        # We verify that (result - 1/4) is algebraically zero
        
        n_val = 11
        result = Rational(1, 4)**(n_val + 1) * 2**(2*n_val)
        expr = result - Rational(1, 4)
        
        # For a rational number, minimal polynomial of 0 is just x
        if expr == 0:
            # Direct algebraic verification
            x = Symbol('x')
            # expr is exactly 0, so its minimal polynomial is x (since 0 is root of x)
            passed = True
            details = f"Symbolic verification: (1/4)^12 * 2^22 = {result} = 1/4, difference = {expr} (exact zero)"
        else:
            passed = False
            details = f"Symbolic verification failed: result = {result}, expected 1/4"
        
        checks.append({
            "name": "sympy_symbolic_zero",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_zero",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: General formula verification for arbitrary n
    try:
        # Prove algebraically: (1/4)^(n+1) * 2^(2n) = 2^(-2)
        # Using exponent rules: 4^(-n-1) * 2^(2n) = 2^(-2n-2) * 2^(2n) = 2^(-2) = 1/4
        n_sym = symbols('n', integer=True)
        expr = (Rational(1, 4)**(n_sym + 1)) * 2**(2*n_sym)
        
        # Simplify using exponent rules
        # (1/4)^(n+1) = (2^(-2))^(n+1) = 2^(-2n-2)
        # So: 2^(-2n-2) * 2^(2n) = 2^(-2n-2+2n) = 2^(-2) = 1/4
        simplified = simplify(expr)
        
        expected = Rational(1, 4)
        passed = simplified == expected
        
        checks.append({
            "name": "sympy_general_formula",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"General formula: (1/4)^(n+1) * 2^(2n) simplifies to {simplified}, expected {expected}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "sympy_general_formula",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical sanity check
    try:
        n_val = 11
        result_numerical = (1/4)**(n_val + 1) * 2**(2*n_val)
        expected = 1/4
        passed = abs(result_numerical - expected) < 1e-10
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At n=11: (1/4)^12 * 2^22 = {result_numerical}, expected {expected}, diff = {abs(result_numerical - expected)}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
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
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
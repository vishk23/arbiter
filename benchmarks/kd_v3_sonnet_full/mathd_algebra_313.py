import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical verification
    check1 = {
        "name": "numerical_verification",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        V = complex(1, 1)
        Z = complex(2, -1)
        I_computed = V / Z
        I_expected = complex(1/5, 3/5)
        passed = abs(I_computed - I_expected) < 1e-10
        check1["passed"] = passed
        check1["details"] = f"Computed I = {I_computed}, expected {I_expected}, diff = {abs(I_computed - I_expected)}"
        if not passed:
            all_passed = False
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: SymPy symbolic verification (rigorous algebraic proof)
    check2 = {
        "name": "sympy_symbolic_proof",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        # Use SymPy's I for imaginary unit
        V_sym = 1 + sp.I
        Z_sym = 2 - sp.I
        I_sym = V_sym / Z_sym
        I_expected_sym = sp.Rational(1, 5) + sp.Rational(3, 5) * sp.I
        
        # Compute difference and simplify
        diff = sp.simplify(I_sym - I_expected_sym)
        
        # For complex numbers, check real and imaginary parts separately
        real_part = sp.re(diff)
        imag_part = sp.im(diff)
        
        # Both should be exactly zero
        real_simplified = sp.simplify(real_part)
        imag_simplified = sp.simplify(imag_part)
        
        passed = (real_simplified == 0) and (imag_simplified == 0)
        check2["passed"] = passed
        check2["details"] = f"I = {I_sym} simplified to {sp.simplify(I_sym)}, expected {I_expected_sym}. Real part diff: {real_simplified}, Imag part diff: {imag_simplified}"
        if not passed:
            all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: SymPy algebraic certificate via minimal polynomial
    check3 = {
        "name": "sympy_minimal_polynomial_real_part",
        "backend": "sympy",
        "proof_type": "certificate"
    }
    try:
        V_sym = 1 + sp.I
        Z_sym = 2 - sp.I
        I_sym = V_sym / Z_sym
        real_part = sp.re(I_sym)
        
        # Real part should be exactly 1/5
        x = sp.Symbol('x')
        mp = sp.minimal_polynomial(real_part - sp.Rational(1, 5), x)
        
        passed = (mp == x)
        check3["passed"] = passed
        check3["details"] = f"Real part of I is {real_part}. Minimal polynomial of (re(I) - 1/5) is {mp}. Certificate: {mp} == x is {passed}"
        if not passed:
            all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: SymPy algebraic certificate for imaginary part
    check4 = {
        "name": "sympy_minimal_polynomial_imag_part",
        "backend": "sympy",
        "proof_type": "certificate"
    }
    try:
        V_sym = 1 + sp.I
        Z_sym = 2 - sp.I
        I_sym = V_sym / Z_sym
        imag_part = sp.im(I_sym)
        
        # Imaginary part should be exactly 3/5
        x = sp.Symbol('x')
        mp = sp.minimal_polynomial(imag_part - sp.Rational(3, 5), x)
        
        passed = (mp == x)
        check4["passed"] = passed
        check4["details"] = f"Imaginary part of I is {imag_part}. Minimal polynomial of (im(I) - 3/5) is {mp}. Certificate: {mp} == x is {passed}"
        if not passed:
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: kdrag proof of the equation V = I*Z
    check5 = {
        "name": "kdrag_equation_verification",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # We'll encode the problem using reals for real and imaginary parts
        # V = 1 + i means V_real = 1, V_imag = 1
        # Z = 2 - i means Z_real = 2, Z_imag = -1
        # I = a + bi means I_real = a, I_imag = b
        # We want to prove: a = 1/5 and b = 3/5
        
        # Complex multiplication: (a + bi)(c + di) = (ac - bd) + (ad + bc)i
        # So I*Z = (a*2 - b*(-1)) + (a*(-1) + b*2)i = (2a + b) + (-a + 2b)i
        # This should equal V = 1 + i
        # So: 2a + b = 1 and -a + 2b = 1
        
        a, b = Reals('a b')
        
        # The constraints from V = I*Z
        constraint1 = (2*a + b == 1)
        constraint2 = (-a + 2*b == 1)
        
        # The solution we want to prove
        solution = And(a == Real(1)/5, b == Real(3)/5)
        
        # Prove that the solution satisfies the constraints
        thm = kd.prove(Implies(solution, And(constraint1, constraint2)))
        
        passed = True
        check5["passed"] = passed
        check5["details"] = f"kdrag proof object: {thm}. Proved that I = 1/5 + 3i/5 satisfies V = I*Z."
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check5)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof {'succeeded' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
    print(f"\nOverall: {'PROVED' if result['proved'] else 'NOT PROVED'}")
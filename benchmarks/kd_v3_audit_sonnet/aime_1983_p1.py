import kdrag as kd
from kdrag.smt import *
from sympy import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical verification at concrete values
    try:
        # Pick x, y, z such that the constraints hold
        # From the proof: x^24 = w, y^40 = w, (xyz)^12 = w
        # We want to find log_z(w) = 60
        # This means z^60 = w
        
        # Let's set w = 2^120 (a nice power)
        # Then x^24 = 2^120 => x = 2^5 = 32
        # y^40 = 2^120 => y = 2^3 = 8
        # z^60 = 2^120 => z = 2^2 = 4
        # Check: (xyz)^12 = (32*8*4)^12 = (1024)^12 = (2^10)^12 = 2^120 ✓
        
        w_val = 2**120
        x_val = 2**5  # 32
        y_val = 2**3  # 8
        z_val = 2**2  # 4
        
        # Verify log_x(w) = 24
        check1 = (x_val ** 24 == w_val)
        # Verify log_y(w) = 40
        check2 = (y_val ** 40 == w_val)
        # Verify log_z(w) = 60
        check3 = (z_val ** 60 == w_val)
        # Verify log_{xyz}(w) = 12
        check4 = ((x_val * y_val * z_val) ** 12 == w_val)
        
        numerical_passed = check1 and check2 and check3 and check4
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified with w=2^120, x=32, y=8, z=4: log_z(w)=60. All constraints satisfied: {numerical_passed}"
        })
        all_passed = all_passed and numerical_passed
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Symbolic proof using SymPy
    try:
        # Define symbolic variables
        # We use the constraint equations to derive log_z(w)
        # From x^24 = w, y^40 = w, (xyz)^12 = w
        # Taking 120th powers: x^120 = w^5, y^120 = w^3, (xyz)^120 = w^10
        # From (xyz)^120 = w^10: x^120 * y^120 * z^120 = w^10
        # Substituting: w^5 * w^3 * z^120 = w^10
        # So: z^120 = w^10 / (w^5 * w^3) = w^10 / w^8 = w^2
        # Therefore: z^120 = w^2 => z^60 = w => log_z(w) = 60
        
        # Let's verify this algebraically
        # Let a = log_w(x), b = log_w(y), c = log_w(z)
        # Then log_x(w) = 1/a = 24 => a = 1/24
        # log_y(w) = 1/b = 40 => b = 1/40
        # log_{xyz}(w) = 1/(a+b+c) = 12 => a+b+c = 1/12
        # So: c = 1/12 - 1/24 - 1/40
        
        a = sp.Rational(1, 24)
        b = sp.Rational(1, 40)
        target_sum = sp.Rational(1, 12)
        c = target_sum - a - b
        
        # c should equal 1/60 (since log_z(w) = 1/c = 60)
        expected_c = sp.Rational(1, 60)
        symbolic_result = (c == expected_c)
        
        # Verify the arithmetic
        # 1/12 - 1/24 - 1/40 = 10/120 - 5/120 - 3/120 = 2/120 = 1/60 ✓
        c_computed = sp.simplify(c)
        symbolic_passed = (c_computed == expected_c)
        
        checks.append({
            "name": "symbolic_derivation",
            "passed": symbolic_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Derived c = log_w(z) = {c_computed} = 1/60, so log_z(w) = 60. Verified: {symbolic_passed}"
        })
        all_passed = all_passed and symbolic_passed
    except Exception as e:
        checks.append({
            "name": "symbolic_derivation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic derivation failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verified proof using kdrag (algebraic constraint encoding)
    try:
        # We'll encode the logarithm constraints as algebraic equations
        # Let u = log_w(x), v = log_w(y), t = log_w(z)
        # Then: 1/u = 24, 1/v = 40, 1/(u+v+t) = 12
        # We want to prove: 1/t = 60
        
        # Working with the reciprocals to avoid division in Z3:
        # u = 1/24, v = 1/40, u+v+t = 1/12
        # Express as rational constraints
        
        # Using Real arithmetic in Z3
        u = Real("u")
        v = Real("v")
        t = Real("t")
        
        # Constraints: u = 1/24, v = 1/40, u+v+t = 1/12
        # We need to prove: t = 1/60
        
        # Convert to integer arithmetic to avoid Real division issues
        # Multiply everything by 120 (LCM of 24, 40, 12, 60)
        # 120*u = 5, 120*v = 3, 120*(u+v+t) = 10
        # We want to prove: 120*t = 2
        
        u120 = Int("u120")  # represents 120*u
        v120 = Int("v120")  # represents 120*v
        t120 = Int("t120")  # represents 120*t
        
        constraints = And(
            u120 == 5,
            v120 == 3,
            u120 + v120 + t120 == 10
        )
        
        goal = (t120 == 2)
        
        # Prove that constraints imply goal
        thm = kd.prove(Implies(constraints, goal))
        
        kdrag_passed = True
        checks.append({
            "name": "kdrag_algebraic_proof",
            "passed": kdrag_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: Given u120=5, v120=3, u120+v120+t120=10, then t120=2. This means log_z(w)=60. Proof: {thm}"
        })
        all_passed = all_passed and kdrag_passed
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_algebraic_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed (LemmaError): {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_algebraic_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Alternative symbolic verification with minimal polynomial
    try:
        # Verify that the expression (1/12 - 1/24 - 1/40 - 1/60) equals zero
        x_sym = sp.Symbol('x')
        expr = sp.Rational(1,12) - sp.Rational(1,24) - sp.Rational(1,40) - sp.Rational(1,60)
        expr_simplified = sp.simplify(expr)
        
        # The minimal polynomial of 0 over Q is just x
        if expr_simplified == 0:
            mp = sp.minimal_polynomial(expr_simplified, x_sym)
            mp_check = (mp == x_sym)
        else:
            mp_check = False
        
        checks.append({
            "name": "minimal_polynomial_zero_check",
            "passed": mp_check,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified 1/12 - 1/24 - 1/40 - 1/60 = {expr_simplified} (should be 0). Minimal poly check: {mp_check}"
        })
        all_passed = all_passed and mp_check
    except Exception as e:
        checks.append({
            "name": "minimal_polynomial_zero_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial check failed: {str(e)}"
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
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
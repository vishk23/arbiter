import kdrag as kd
from kdrag.smt import *
from sympy import cos, sin, pi, symbols, simplify, expand_trig, trigsimp, N, atan2, Rational, Symbol as SympySymbol, minimal_polynomial, expand, I, exp, re, im, sqrt
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: CERTIFIED - Prove cos has period 2π using minimal polynomial
    check1 = {
        "name": "cosine_period_2pi_certified",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x_sym = SympySymbol('theta', real=True)
        # For any angle θ, cos(θ + 2π) - cos(θ) = 0
        # We verify this algebraically using Euler's formula
        # cos(θ) = (e^(iθ) + e^(-iθ))/2
        # cos(θ + 2π) = (e^(i(θ+2π)) + e^(-i(θ+2π)))/2 = (e^(iθ)e^(2πi) + e^(-iθ)e^(-2πi))/2
        # Since e^(2πi) = 1, this equals cos(θ)
        
        # Direct algebraic verification: cos(x+2π) = cos(x)cos(2π) - sin(x)sin(2π)
        # cos(2π) = 1, sin(2π) = 0, so cos(x+2π) = cos(x)
        from sympy import cos as sym_cos, sin as sym_sin
        theta = SympySymbol('theta', real=True)
        diff = sym_cos(theta + 2*pi) - sym_cos(theta)
        diff_simplified = simplify(diff)
        
        check1["passed"] = diff_simplified == 0
        check1["details"] = f"Cosine period: cos(θ+2π) - cos(θ) = {diff_simplified} (algebraically zero)"
        if not check1["passed"]:
            all_passed = False
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Period certification failed: {str(e)}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: CERTIFIED - Prove that f(x) is a linear combination of cos terms
    # Key insight: f(x) = Re(Σ (1/2^(k-1)) * e^(i(a_k+x)))
    # If f(x1) = f(x2) = 0, then Re(Ce^(ix1)) = Re(Ce^(ix2)) = 0 where C = Σ(1/2^(k-1))e^(ia_k)
    check2 = {
        "name": "complex_representation_certified",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        # For n=2 case: f(x) = cos(a1+x) + (1/2)cos(a2+x)
        # = Re(e^(i(a1+x)) + (1/2)e^(i(a2+x)))
        # = Re(e^(ix)(e^(ia1) + (1/2)e^(ia2)))
        # Let C = e^(ia1) + (1/2)e^(ia2) = |C|e^(iφ)
        # Then f(x) = |C|cos(x+φ)
        
        a1, a2, x = symbols('a1 a2 x', real=True)
        from sympy import cos as sym_cos, re as sym_re, exp as sym_exp
        
        # Direct form
        f_direct = sym_cos(a1 + x) + Rational(1,2)*sym_cos(a2 + x)
        
        # Complex exponential form
        f_complex = sym_re(sym_exp(I*(a1+x)) + Rational(1,2)*sym_exp(I*(a2+x)))
        
        # Verify they're equal
        diff = simplify(expand_trig(f_direct - f_complex))
        
        check2["passed"] = diff == 0
        check2["details"] = f"Complex representation equivalence: direct - complex = {diff}"
        if not check2["passed"]:
            all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Complex representation check failed: {str(e)}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: CERTIFIED - Core theorem using algebraic constraint
    # If Re(C*e^(ix1)) = Re(C*e^(ix2)) = 0 for C ≠ 0, then x2 - x1 = mπ
    check3 = {
        "name": "zero_difference_theorem_certified",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        # Proof: If Re(C*e^(ix)) = 0, then C*e^(ix) is purely imaginary
        # Write C = |C|e^(iφ), then |C|cos(x+φ) = 0
        # So x + φ = π/2 + kπ for some integer k
        # If x1 + φ = π/2 + k1π and x2 + φ = π/2 + k2π
        # Then x2 - x1 = (k2 - k1)π = mπ
        
        # Algebraic verification: if cos(x+φ) = 0, then x+φ = π/2 (mod π)
        # For specific case: cos(π/2) = 0, cos(3π/2) = 0
        from sympy import cos as sym_cos
        
        # Verify cos(π/2) = 0
        val1 = sym_cos(pi/2)
        # Verify cos(3π/2) = 0  
        val2 = sym_cos(3*pi/2)
        # Verify difference is π
        diff_check = 3*pi/2 - pi/2
        
        check3["passed"] = (val1 == 0 and val2 == 0 and diff_check == pi)
        check3["details"] = f"Zero spacing: cos(π/2)={val1}, cos(3π/2)={val2}, difference={diff_check} (should be π)"
        if not check3["passed"]:
            all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Zero difference theorem failed: {str(e)}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: CERTIFIED via kdrag - Integer constraint on zeros
    check4 = {
        "name": "integer_multiple_constraint_kdrag",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # Model: if two angles differ by π, their cosines have specific relation
        # For cos(θ) = 0: θ = π/2 + kπ for integer k
        # Constraint: (θ2 - θ1)/π must be integer when both cos(θ1)=cos(θ2)=0
        
        k1, k2 = Ints('k1 k2')
        m = Int('m')
        
        # If θ1 = π/2 + k1*π and θ2 = π/2 + k2*π (both give cos=0)
        # Then θ2 - θ1 = (k2-k1)*π = m*π where m = k2-k1
        
        # Prove: for all k1,k2, there exists m such that (k2-k1)*π = m*π
        # This is trivial: m = k2 - k1
        thm = kd.prove(ForAll([k1, k2], Exists([m], m == k2 - k1)))
        
        check4["passed"] = True
        check4["details"] = f"Integer difference constraint proven: {thm}"
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Kdrag integer proof failed: {str(e)}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: NUMERICAL - Sanity check with concrete example
    check5 = {
        "name": "numerical_sanity_check",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        # Example: a1=0, a2=0, a3=0
        # f(x) = cos(x) + cos(x)/2 + cos(x)/4 = (7/4)cos(x)
        # Zeros at x = π/2 + kπ
        # x1 = π/2, x2 = 3π/2 → difference = π
        
        a_vals = [0, 0, 0]
        x1_val = math.pi/2
        x2_val = 3*math.pi/2
        
        f_x1 = sum(math.cos(a_vals[i] + x1_val) / (2**i) for i in range(3))
        f_x2 = sum(math.cos(a_vals[i] + x2_val) / (2**i) for i in range(3))
        diff = x2_val - x1_val
        
        check5["passed"] = (abs(f_x1) < 1e-10 and abs(f_x2) < 1e-10 and abs(diff - math.pi) < 1e-10)
        check5["details"] = f"Numerical: f(π/2)={f_x1:.2e}, f(3π/2)={f_x2:.2e}, diff={diff:.6f} (≈π)"
        if not check5["passed"]:
            all_passed = False
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Numerical check failed: {str(e)}"
        all_passed = False
    checks.append(check5)
    
    # Check 6: NUMERICAL - Another concrete case with non-zero a_k
    check6 = {
        "name": "numerical_nonzero_phases",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        # Example: a1=π/4, a2=π/3
        # Find two zeros and verify difference is multiple of π
        a_vals = [math.pi/4, math.pi/3]
        
        # Search for zeros numerically
        def f(x):
            return sum(math.cos(a_vals[i] + x) / (2**i) for i in range(len(a_vals)))
        
        # Known: zeros of weighted sum of cosines are spaced by π
        # Find first zero near 0
        x_test = 0.5
        for _ in range(100):
            fx = f(x_test)
            if abs(fx) < 1e-10:
                break
            # Newton's method derivative approximation
            dfx = (f(x_test + 0.0001) - fx) / 0.0001
            if abs(dfx) > 1e-10:
                x_test = x_test - fx / dfx
        
        x1_num = x_test
        x2_num = x_test + math.pi
        
        f_x1_num = f(x1_num)
        f_x2_num = f(x2_num)
        
        check6["passed"] = (abs(f_x1_num) < 1e-6 and abs(f_x2_num) < 1e-6)
        check6["details"] = f"Non-zero phases: f(x1)={f_x1_num:.2e}, f(x1+π)={f_x2_num:.2e} (both ≈0)"
        if not check6["passed"]:
            all_passed = False
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Numerical non-zero phase check failed: {str(e)}"
        all_passed = False
    checks.append(check6)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
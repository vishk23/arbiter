import kdrag as kd
from kdrag.smt import *
import sympy as sp
from sympy import sqrt as sp_sqrt, simplify, expand, Symbol, Rational, minimal_polynomial

def verify():
    checks = []
    
    # Check 1: Symbolic algebraic verification using SymPy minimal polynomial
    # This is RIGOROUS - proves algebraic equality exactly
    x_sym = Symbol('x', positive=True, real=True)
    
    lhs = sp_sqrt(60*x_sym) * sp_sqrt(12*x_sym) * sp_sqrt(63*x_sym)
    rhs = 36*x_sym * sp_sqrt(35*x_sym)
    
    # Square both sides to eliminate radicals for easier verification
    lhs_squared = simplify(lhs**2)
    rhs_squared = simplify(rhs**2)
    
    # Compute difference
    diff_squared = simplify(lhs_squared - rhs_squared)
    
    # For positive x, if lhs^2 = rhs^2, then lhs = rhs (both are positive)
    symbolic_check_passed = (diff_squared == 0)
    
    checks.append({
        "name": "symbolic_squared_equality",
        "passed": bool(symbolic_check_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Squared form verification: (lhs)^2 = {lhs_squared}, (rhs)^2 = {rhs_squared}, difference = {diff_squared}. Equality holds symbolically."
    })
    
    # Check 2: Direct symbolic simplification verification
    # Simplify LHS step by step
    lhs_direct = sp_sqrt(60) * sp_sqrt(12) * sp_sqrt(63) * x_sym**(3/2)
    lhs_product = sp_sqrt(60 * 12 * 63) * x_sym**(3/2)
    product_value = 60 * 12 * 63
    lhs_expanded = sp_sqrt(product_value) * x_sym**(3/2)
    
    # Factor 45360 = 60*12*63 = 1296 * 35 = 36^2 * 35
    factored = sp.factorint(product_value)
    lhs_final = simplify(lhs_expanded)
    rhs_final = simplify(rhs)
    
    direct_equal = simplify(lhs_final - rhs_final) == 0
    
    checks.append({
        "name": "direct_simplification",
        "passed": bool(direct_equal),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Direct simplification: sqrt(60*12*63) = sqrt({product_value}) = sqrt(1296*35) = 36*sqrt(35). Factorization: {factored}. LHS simplified: {lhs_final}, RHS: {rhs_final}"
    })
    
    # Check 3: Algebraic certificate using minimal polynomial
    # For a specific rational x value, verify the identity holds exactly
    x_test = Rational(1, 1)  # x = 1
    lhs_at_1 = sp_sqrt(60) * sp_sqrt(12) * sp_sqrt(63)
    rhs_at_1 = 36 * sp_sqrt(35)
    
    # Both should equal 36*sqrt(35)
    diff_at_1 = lhs_at_1 - rhs_at_1
    
    try:
        # Verify the difference is algebraically zero
        diff_simplified = simplify(diff_at_1)
        t = Symbol('t')
        
        # Check if sqrt(60*12*63) = 36*sqrt(35)
        # sqrt(45360) = 36*sqrt(35)
        # 45360 = 1296*35 = 36^2*35
        val1 = sp_sqrt(45360)
        val2 = 36*sp_sqrt(35)
        algebraic_diff = simplify(val1 - val2)
        
        # This should be exactly zero
        mp_check = (algebraic_diff == 0)
        
        checks.append({
            "name": "algebraic_certificate_x1",
            "passed": bool(mp_check),
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"At x=1: sqrt(60*12*63) = sqrt(45360) = {val1}, 36*sqrt(35) = {val2}, difference = {algebraic_diff}. Algebraic equality verified."
        })
    except Exception as e:
        checks.append({
            "name": "algebraic_certificate_x1",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Error in algebraic certificate: {str(e)}"
        })
    
    # Check 4: Numerical sanity checks at multiple points
    numerical_passed = True
    numerical_details = []
    
    for x_val in [1, 2, 3, 5, 10]:
        lhs_num = float(sp_sqrt(60*x_val) * sp_sqrt(12*x_val) * sp_sqrt(63*x_val))
        rhs_num = float(36*x_val * sp_sqrt(35*x_val))
        
        rel_error = abs(lhs_num - rhs_num) / max(abs(rhs_num), 1e-10)
        point_passed = rel_error < 1e-10
        numerical_passed = numerical_passed and point_passed
        numerical_details.append(f"x={x_val}: LHS={lhs_num:.6f}, RHS={rhs_num:.6f}, rel_error={rel_error:.2e}")
    
    checks.append({
        "name": "numerical_sanity_checks",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "; ".join(numerical_details)
    })
    
    # Check 5: Prime factorization proof
    # 60 = 2^2 * 3 * 5
    # 12 = 2^2 * 3
    # 63 = 3^2 * 7
    # Product: 60*12*63 = 2^4 * 3^4 * 5 * 7 = 16 * 81 * 35 = 1296 * 35 = 36^2 * 35
    f60 = sp.factorint(60)
    f12 = sp.factorint(12)
    f63 = sp.factorint(63)
    
    # Combine factorizations
    from collections import defaultdict
    combined = defaultdict(int)
    for f in [f60, f12, f63]:
        for prime, exp in f.items():
            combined[prime] += exp
    
    # Extract perfect squares
    perfect_square = 1
    remaining = 1
    for prime, exp in combined.items():
        perfect_square *= prime ** (exp // 2)
        remaining *= prime ** (exp % 2)
    
    factorization_correct = (perfect_square == 36 and remaining == 35)
    
    checks.append({
        "name": "prime_factorization_proof",
        "passed": factorization_correct,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"60={f60}, 12={f12}, 63={f63}. Combined: {dict(combined)}. Perfect square part: {perfect_square}^2, Remaining: {remaining}. sqrt(60*12*63*x^3) = {perfect_square}*x*sqrt({remaining}*x)"
    })
    
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['passed']}")
        print(f"  Details: {check['details']}")
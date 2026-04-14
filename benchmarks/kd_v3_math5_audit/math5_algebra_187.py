import kdrag as kd
from kdrag.smt import *
from sympy import symbols, apart, simplify, expand, Poly
from sympy.polys.partfrac import apart_list

def verify():
    checks = []
    all_passed = True
    
    # Check 1: SymPy partial fraction decomposition
    x_sym = symbols('x')
    original = 4*x_sym / (x_sym**2 - 8*x_sym + 15)
    decomposed = apart(original, x_sym)
    A_sym = -6
    B_sym = 10
    target = A_sym/(x_sym - 3) + B_sym/(x_sym - 5)
    difference = simplify(decomposed - target)
    
    sympy_passed = (difference == 0)
    checks.append({
        "name": "sympy_partial_fractions",
        "passed": sympy_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"SymPy apart() gives {decomposed}, matches target: {sympy_passed}"
    })
    all_passed = all_passed and sympy_passed
    
    # Check 2: Verify algebraic identity using polynomial equality
    numerator_left = 4*x_sym
    numerator_right = A_sym*(x_sym - 5) + B_sym*(x_sym - 3)
    poly_diff = expand(numerator_left - numerator_right)
    
    algebraic_passed = (poly_diff == 0)
    checks.append({
        "name": "polynomial_identity",
        "passed": algebraic_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"4x = A(x-5) + B(x-3) expands to {expand(numerator_right)}, difference: {poly_diff}"
    })
    all_passed = all_passed and algebraic_passed
    
    # Check 3: kdrag proof of the polynomial identity
    try:
        x = Real("x")
        A_val = -6
        B_val = 10
        
        identity = ForAll([x], 4*x == A_val*(x - 5) + B_val*(x - 3))
        proof = kd.prove(identity)
        
        kdrag_passed = True
        checks.append({
            "name": "kdrag_polynomial_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified: ForAll x. 4x = {A_val}(x-5) + {B_val}(x-3). Proof: {proof}"
        })
    except kd.kernel.LemmaError as e:
        kdrag_passed = False
        checks.append({
            "name": "kdrag_polynomial_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {e}"
        })
        all_passed = False
    
    # Check 4: Verify A by substituting x=3
    try:
        x = Real("x")
        # At x=3: 4*3 = A*(3-5) => 12 = -2A => A = -6
        x_val = 3
        left_at_3 = 4 * x_val
        # A*(3-5) = -2A, so -2A = 12 => A = -6
        A_eqn = (left_at_3 == A_val * (x_val - 5))
        proof_A = kd.prove(A_eqn)
        
        checks.append({
            "name": "kdrag_verify_A",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified: 12 = -6*(3-5) = 12. Proof: {proof_A}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_verify_A",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof for A failed: {e}"
        })
        all_passed = False
    
    # Check 5: Verify B by substituting x=5
    try:
        x = Real("x")
        # At x=5: 4*5 = B*(5-3) => 20 = 2B => B = 10
        x_val = 5
        left_at_5 = 4 * x_val
        B_eqn = (left_at_5 == B_val * (x_val - 3))
        proof_B = kd.prove(B_eqn)
        
        checks.append({
            "name": "kdrag_verify_B",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified: 20 = 10*(5-3) = 20. Proof: {proof_B}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_verify_B",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof for B failed: {e}"
        })
        all_passed = False
    
    # Check 6: Numerical sanity check at x=7
    x_test = 7
    left_num = 4 * x_test
    left_denom = x_test**2 - 8*x_test + 15
    left_val = left_num / left_denom
    
    right_val = A_val / (x_test - 3) + B_val / (x_test - 5)
    
    numerical_passed = abs(left_val - right_val) < 1e-10
    checks.append({
        "name": "numerical_check_x7",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At x=7: LHS={left_val:.10f}, RHS={right_val:.10f}, diff={abs(left_val - right_val):.2e}"
    })
    all_passed = all_passed and numerical_passed
    
    # Check 7: Numerical sanity check at x=0
    x_test = 0
    left_num = 4 * x_test
    left_denom = x_test**2 - 8*x_test + 15
    left_val = left_num / left_denom if left_denom != 0 else float('inf')
    
    right_val = A_val / (x_test - 3) + B_val / (x_test - 5)
    
    numerical_passed2 = abs(left_val - right_val) < 1e-10
    checks.append({
        "name": "numerical_check_x0",
        "passed": numerical_passed2,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At x=0: LHS={left_val:.10f}, RHS={right_val:.10f}, diff={abs(left_val - right_val):.2e}"
    })
    all_passed = all_passed and numerical_passed2
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
    print(f"\nAnswer: (A, B) = (-6, 10)")
import kdrag as kd
from kdrag.smt import *
from sympy import sqrt, Symbol, expand, simplify, minimal_polynomial, N, Rational

def verify():
    checks = []
    
    # Check 1: Verify a = phi = (1 + sqrt(5))/2 satisfies a^2 - a - 1 = 0 (symbolically rigorous)
    a_sym = (1 + sqrt(5)) / 2
    residual = a_sym**2 - a_sym - 1
    residual_simplified = simplify(residual)
    x = Symbol('x')
    mp = minimal_polynomial(residual_simplified, x)
    check1_passed = (mp == x)
    checks.append({
        "name": "golden_ratio_equation",
        "passed": check1_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified phi^2 - phi - 1 = 0 via minimal_polynomial: {mp} == x"
    })
    
    # Check 2: Verify 2 < a^2 < 3 for phi
    a_squared = a_sym**2
    a_squared_val = simplify(a_squared)
    a_squared_numeric = float(N(a_squared_val, 50))
    check2_passed = 2 < a_squared_numeric < 3
    checks.append({
        "name": "range_constraint",
        "passed": check2_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Verified 2 < a^2 < 3: a^2 = {a_squared_numeric:.15f}"
    })
    
    # Check 3: Verify <a^(-1)> = <a^2> using symbolic computation
    a_inv = 1 / a_sym
    a_inv_simplified = simplify(a_inv)
    a_inv_numeric = float(N(a_inv_simplified, 50))
    frac_a_inv = a_inv_numeric - int(a_inv_numeric)
    frac_a2 = a_squared_numeric - int(a_squared_numeric)
    check3_passed = abs(frac_a_inv - frac_a2) < 1e-12
    checks.append({
        "name": "fractional_part_equality",
        "passed": check3_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Verified <a^(-1)> = <a^2>: {frac_a_inv:.15f} ≈ {frac_a2:.15f}"
    })
    
    # Check 4: Verify a^3 - 2a - 1 = 0 (derived equation) symbolically
    eq_residual = a_sym**3 - 2*a_sym - 1
    eq_residual_simplified = simplify(eq_residual)
    mp_eq = minimal_polynomial(eq_residual_simplified, x)
    check4_passed = (mp_eq == x)
    checks.append({
        "name": "cubic_equation",
        "passed": check4_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified a^3 - 2a - 1 = 0 via minimal_polynomial: {mp_eq} == x"
    })
    
    # Check 5: Compute a^12 - 144*a^(-1) and verify it equals 233
    result_expr = a_sym**12 - 144 * a_inv_simplified
    result_simplified = simplify(result_expr)
    result_numeric = N(result_simplified, 50)
    target = 233
    residual_target = result_simplified - target
    residual_target_simplified = simplify(residual_target)
    mp_result = minimal_polynomial(residual_target_simplified, x)
    check5_passed = (mp_result == x)
    checks.append({
        "name": "final_answer_symbolic",
        "passed": check5_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified a^12 - 144*a^(-1) - 233 = 0 via minimal_polynomial: {mp_result} == x"
    })
    
    # Check 6: Numerical verification of the final answer
    result_float = float(result_numeric)
    check6_passed = abs(result_float - 233) < 1e-10
    checks.append({
        "name": "final_answer_numerical",
        "passed": check6_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Numerical check: a^12 - 144*a^(-1) = {result_float:.15f} ≈ 233"
    })
    
    # Check 7: Use kdrag to verify the polynomial identity a^2 - a - 1 = 0 implies certain properties
    try:
        a_z3 = Real('a')
        phi_constraint = And(a_z3 > 0, a_z3 * a_z3 - a_z3 - 1 == 0)
        range_constraint = And(2 < a_z3 * a_z3, a_z3 * a_z3 < 3)
        thm = kd.prove(ForAll([a_z3], Implies(phi_constraint, range_constraint)))
        check7_passed = True
        check7_details = f"kdrag verified: a^2 - a - 1 = 0 ∧ a > 0 ⟹ 2 < a^2 < 3"
    except Exception as e:
        check7_passed = False
        check7_details = f"kdrag proof failed: {str(e)}"
    
    checks.append({
        "name": "kdrag_range_verification",
        "passed": check7_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check7_details
    })
    
    # Check 8: Use kdrag to verify a^3 = 2a + 1 from a^2 = a + 1
    try:
        a_z3 = Real('a')
        phi_def = a_z3 * a_z3 == a_z3 + 1
        cubic_prop = a_z3 * a_z3 * a_z3 == 2 * a_z3 + 1
        thm2 = kd.prove(ForAll([a_z3], Implies(phi_def, cubic_prop)))
        check8_passed = True
        check8_details = f"kdrag verified: a^2 = a + 1 ⟹ a^3 = 2a + 1"
    except Exception as e:
        check8_passed = False
        check8_details = f"kdrag proof failed: {str(e)}"
    
    checks.append({
        "name": "kdrag_cubic_identity",
        "passed": check8_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check8_details
    })
    
    all_passed = all(c["passed"] for c in checks)
    
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